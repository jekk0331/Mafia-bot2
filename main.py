import asyncio
import time
import aiosqlite
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from aiogram.fsm.storage.memory import MemoryStorage

# 1. BOT TOKENINGIZNI SHU YERGA YOZING
BOT_TOKEN ="8861451228:AAFrs5MHO2Ahyc0eWGjxIbUCCnW3QhlEjEs"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DB_PATH = "mafia_bot.db"
active_games = {}

# ==========================================
# 1. MA'LUMOTLAR BAZASI (SQLite)
# ==========================================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                coins INTEGER DEFAULT 500,
                gems INTEGER DEFAULT 10,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                night_time INTEGER DEFAULT 45,
                vote_time INTEGER DEFAULT 40
            )
        """)
        await db.commit()

async def get_user_data(user_id: int, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, gems, wins, losses FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await db.execute(
                    "INSERT INTO users (user_id, full_name, coins, gems, wins, losses) VALUES (?, ?, 500, 10, 0, 0)",
                    (user_id, full_name)
                )
                await db.commit()
                return (500, 10, 0, 0)
            return row

# ==========================================
# 2. JIMLIK (MUTE) MIDDLEWARE FILTRI
# ==========================================
class SilenceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data):
        if isinstance(event, types.Message) and event.chat.type in ["group", "supergroup"]:
            chat_id = event.chat.id
            user_id = event.from_user.id
            game = active_games.get(chat_id)

            if game and game.get("status") == "playing":
                is_dead = user_id in game.get("dead_players", [])
                is_night = game.get("phase") == "night"

                if is_dead or is_night:
                    try:
                        await event.delete()
                        await event.bot.restrict_chat_member(
                            chat_id=chat_id,
                            user_id=user_id,
                            permissions=ChatPermissions(can_send_messages=False),
                            until_date=int(time.time()) + 60
                        )
                    except Exception:
                        pass
                    return
        return await handler(event, data)

dp.message.outer_middleware(SilenceMiddleware())

# ==========================================
# 3. FOYDALANUVCHI BUYRUQLARI (/start, /profile, /shop, /top)
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await get_user_data(message.from_user.id, message.from_user.full_name)
    await message.answer("🎮 **Pro MAFIYA Botiga xush kelibsiz!**\n\nBotni guruhingizga qo'shing va admin huquqini bering.")

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    data = await get_user_data(message.from_user.id, message.from_user.full_name)
    text = (
        f"👤 **Foydalanuvchi profili:** {message.from_user.full_name}\n\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"💰 Tangalar: **{data[0]}**\n"
        f"💎 Olmoslar: **{data[1]}**\n\n"
        f"🏆 G'alabalar: **{data[2]}**\n"
        f"💀 Mag'lubiyatlar: **{data[3]}**"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    text = (
        "🛒 **Mafiya Do'koni**\n\n"
        "🛡 **Himoya** — 100 tanga\n"
        "🎭 **Maska** — 150 tanga\n"
        "🔫 **Qurol** — 300 tanga"
    )
    await message.answer(text)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    await message.answer("🏆 **Top O'yinchilar:**\n\n1. Jasur — 150 g'alaba\n2. Anvar — 120 g'alaba")

# ==========================================
# 4. GURUH SOZLAMALARI (/settings)
# ==========================================
@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    text = (
        "⚙️ **Guruh sozlamalari**\n\n"
        "Quyidagi bo'limlardan birini tanlang:\n\n"
        "⏰ **Vaqt sozlamalari** — tun, kunduz, tasdiqlash va so'nggi so'z vaqtlari\n"
        "▶️ **O'yinni boshlash** — kim ro'yxatdan o'tadi/boshlaydi\n"
        "🎭 **Rollar** — qo'shimcha rollarni yoqish/o'chirish\n"
        "🎁 **Buyum funksiyalari** — do'kondagi buyumlar\n"
        "📢 **Jimlik** — o'lganlar va tun rejimida yozish taqig'i\n"
        "🛹 **Boshqa** — animatsiyalar va xush kelibsiz xabari"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Vaqt sozlamalari", callback_data="grp_set_time")],
        [InlineKeyboardButton(text="▶️ O'yinni boshlash sozlamalari", callback_data="grp_set_start")],
        [InlineKeyboardButton(text="🎭 Rollar", callback_data="grp_set_roles")],
        [InlineKeyboardButton(text="🎁 Buyum funksiyalari", callback_data="grp_set_items")],
        [InlineKeyboardButton(text="📢 Jimlik", callback_data="grp_set_silence")],
        [InlineKeyboardButton(text="🛹 Boshqa", callback_data="grp_set_other")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "grp_settings_main")
async def process_grp_main(callback: types.CallbackQuery):
    text = "⚙️ **Guruh sozlamalari**\n\nBo'limni tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Vaqt sozlamalari", callback_data="grp_set_time")],
        [InlineKeyboardButton(text="▶️ O'yinni boshlash sozlamalari", callback_data="grp_set_start")],
        [InlineKeyboardButton(text="🎭 Rollar", callback_data="grp_set_roles")],
        [InlineKeyboardButton(text="🎁 Buyum funksiyalari", callback_data="grp_set_items")],
        [InlineKeyboardButton(text="📢 Jimlik", callback_data="grp_set_silence")],
        [InlineKeyboardButton(text="🛹 Boshqa", callback_data="grp_set_other")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "grp_set_time")
async def process_grp_time(callback: types.CallbackQuery):
    text = (
        "⏰ **Vaqt sozlamalari**\n\n"
        "📜 Ro'yxatdan o'tish: **45 soniya**\n"
        "🎆 Tun davomiyligi: **45 soniya**\n"
        "☀️ Ovoz berish vaqti: **40 soniya**\n"
        "⚖️ Tasdiqlash vaqti: **20 soniya**\n"
        "⚰️ So'nggi so'z vaqti: **45 soniya**"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="grp_settings_main")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "grp_set_roles")
async def process_grp_roles(callback: types.CallbackQuery):
    text = (
        "🎭 **Rollar**\n\n"
        "Asosiy rollar (Don, Mafiya, Komissar, Doktor) doim yoqilgan.\n"
        "Qo'shimcha rollarni boshqarishingiz mumkin:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💃 Kezuvchi: ✅ Yoqilgan", callback_data="toggle_role")],
        [InlineKeyboardButton(text="🍾 Daydi: ✅ Yoqilgan", callback_data="toggle_role")],
        [InlineKeyboardButton(text="⛏ Konchi: ✅ Yoqilgan", callback_data="toggle_role")],
        [InlineKeyboardButton(text="📦 Minior: ✅ Yoqilgan", callback_data="toggle_role")],
        [InlineKeyboardButton(text="🧙‍♂️ Afsungar: ✅ Yoqilgan", callback_data="toggle_role")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="grp_settings_main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "grp_set_silence")
async def process_grp_silence(callback: types.CallbackQuery):
    text = (
        "📢 **Jimlik**\n\n"
        "💀 O'lganlar uchun: ❌ O'chirilgan\n"
        "😴 Uxlayotganlar uchun: ❌ O'chirilgan\n"
        "👀 O'ynamayotganlar uchun: ❌ O'chirilgan\n"
        "🌙 Tun vaqtida (hammaga): ❌ O'chirilgan"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="grp_settings_main")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "grp_set_other")
async def process_grp_other(callback: types.CallbackQuery):
    text = "🛹 **Boshqa sozlamalar**\n\n🎬 Tungi animatsiya: 🟩 Yoqilgan\n💘 Xush kelibsiz xabari: ❌ O'chirilgan"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="grp_settings_main")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

# ==========================================
# 5. ADMIN PANEL (/admin)
# ==========================================
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    text = "⚙️ **Admin Panel**\n\nKerakli bo'limni tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔮 Klanlar", callback_data="adm_clan")],
        [InlineKeyboardButton(text="🎁 Daraja gift", callback_data="adm_gift")],
        [InlineKeyboardButton(text="🛠 Texnik ishlar", callback_data="adm_maint")],
        [InlineKeyboardButton(text="🍕 Premium emoji", callback_data="adm_emoji")],
        [InlineKeyboardButton(text="🔐 Qo'shimcha adminlar", callback_data="adm_extra")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

# ==========================================
# 6. O'YIN TIZIMI (/game)
# ==========================================
@dp.message(Command("game"))
async def cmd_game(message: types.Message):
    if message.chat.type == "private":
        await message.answer("❌ O'yinni faqat guruhlarda boshlash mumkin!")
        return

    chat_id = message.chat.id
    active_games[chat_id] = {
        "status": "playing",
        "phase": "registration",
        "players": [message.from_user.id],
        "dead_players": []
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qatnashish", callback_data="join_game")],
        [InlineKeyboardButton(text="▶️ O'yinni boshlash", callback_data=f"run_night_{chat_id}")]
    ])
    await message.answer("🎮 **Mafiya o'yiningizga ro'yxatdan o'tish boshlandi!**", reply_markup=kb)

@dp.callback_query(F.data.startswith("run_night_"))
async def process_run_night(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[2])
    if chat_id in active_games:
        active_games[chat_id]["phase"] = "night"
    await callback.message.edit_text("🌙 **Tun tushdi!** Shahar aholisi uyquga ketdi...")

# ==========================================
# BOTNI ISHGA TUSHIRISH
# ==========================================
async def main():
    await init_db()
    print("Mafiya bot barcha funksiyalar bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
