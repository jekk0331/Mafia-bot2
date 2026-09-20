import asyncio
import logging
import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.fsm.storage.memory import MemoryStorage

# ================= 1. RENDER UCHUN PORT SERVERI =================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Pro Mafia Bot 24/7 Live!")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# ================= 2. BOT SOZLAMALARI =================
BOT_TOKEN = os.environ.get("8861451228:AAHajj0yFyXyqWfWpNtNtEubkvVm5-wL2_Y") # O'zingizning tokeningiz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= 3. BARCHA 32 TA ROLLAR RO'YXATI =================
ROLES = {
    # Tinch fuqarolar (14 ta)
    "tinch": "👨‍🌾 Tinch aholi",
    "komissar": "🕵️‍♂️ Komissar (Sherif)",
    "doktor": "👨‍⚕️ Shifokor",
    "serjant": "👮‍♂️ Serjant",
    "mantiqchi": "🧠 Mantiqchi",
    "lover": "💃 Ajoyib qiz",
    "detektiv": "🔎 Detektiv",
    "hamshira": "👩‍⚕️ Hamshira",
    "aygoqchi": "🕵️ Ayg'oqchi",
    "suvchi": "🌊 Suvchi",
    "ot_ochiruvchi": "👨‍🚒 O't o'chiruvchi",
    "qutqaruvchi": "🛟 Qutqaruvchi",
    "xaker": "💻 Xaker",
    "mer": "🎩 Mer",

    # Mafiya va Qotillar (11 ta)
    "mafia": "🕶 Mafiya",
    "don": "👑 Mafiya Doni",
    "qotil": "🔪 Qotil",
    "advokat": "💼 Advokat",
    "shapoklyak": "👵 Shapoklyak",
    "qora_beva": "🕷 Qora beva",
    "snayper": "🎯 Snayper",
    "terrorchi": "💣 Terrorchi",
    "ninja": "🥷 Ninja",
    "ogri": "🦹 O'g'ri",
    "yollanma": "🏹 Yollanma qotil",

    # Neytral va Maxsus rollar (7 ta)
    "kamikadze": "💥 Kamikadze",
    "maniak": "🪓 Maniak",
    "joker": "🃏 Joker",
    "psix": "🧪 Psixopat",
    "aleks": "🌀 Amneziya (Aleks)",
    "klon": "🪞 Klon",
    "ozga_sayyoralik": "👽 O'zga sayyoralik"
}

# ================= 4. MA'LUMOTLAR BAZASI VA O'YIN TIZIMI =================
USERS_DB = {}   # user_id -> {balance, diamonds, vip, wins, games}
GAMES = {}      # chat_id -> {players: {}, status: "waiting/playing", phase: ""}

def get_user(user_id, name="O'yinchi"):
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "name": name,
            "coins": 500,
            "diamonds": 10,
            "vip": False,
            "wins": 0,
            "games": 0,
            "last_bonus": 0
        }
    return USERS_DB[user_id]

# ================= 5. ASOSIY MENYU TUGMALARI =================
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Shaxsiy kabinet", callback_data="shaxsiy_kabinet")
        ],
        [
            InlineKeyboardButton(text="🤖 Botni guruhga qo'sh➕", url="https://t.me/ProMafiaBot?startgroup=true"),
            InlineKeyboardButton(text="👁 Yangiliklar", url="https://t.me/telegram")
        ],
        [
            InlineKeyboardButton(text="🎲 O'yin guruhlari", callback_data="game_groups")
        ],
        [
            InlineKeyboardButton(text="🎁 Kunlik bonus", callback_data="daily_bonus")
        ],
        [
            InlineKeyboardButton(text="💳 Profilim", callback_data="profile"),
            InlineKeyboardButton(text="📑 O'yin qoidalari", callback_data="rules")
        ],
        [
            InlineKeyboardButton(text="🏆 Top o'yinchilar", callback_data="top_players")
        ]
    ])

# ================= 6. SHAXSIY CHAT BUYRUQLARI =================
@dp.message(Command("start"), F.chat.type == "private")
async def cmd_start_private(message: Message):
    get_user(message.from_user.id, message.from_user.first_name)
    await message.answer(
        f"Salom, {message.from_user.first_name}!\nMen 🏰 **Pro Mafia** rasmiy botiman.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "❓ **Buyruqlar ro'yxati**\n\n"
        "🎮 **O'yin**\n"
        "/game — Ro'yxatdan o'tishni boshlash (Guruhda)\n"
        "/start — O'yinni boshlash (Guruhda)\n"
        "/stop — O'yinni to'xtatish (Admin)\n"
        "/extend — Ro'yxatdan o'tish vaqtini uzaytirish\n"
        "/kick — O'yinchini chiqarib tashlash\n"
        "/leave — O'yindan chiqish (VIP)\n"
        "/my_role — Joriy o'yindagi rolingiz\n"
        "/roles — Barcha 32 ta rollar ro'yxati\n"
        "/top — Top o'yinchilar\n\n"
        "💰 **Pul va VIP**\n"
        "/profile — Balans va statistika\n"
        "/pro — VIP status sotib olish\n"
        "/give — Olmos sovg'a qilish\n"
        "/pulyubor — Tanga yuborish\n"
        "/gifts — Daraja mukofotlari\n\n"
        "🛡 **Moderatsiya**\n"
        "/mute, /unmute — Guruhda jimlatish\n"
        "/ban, /unban — Bloklash\n"
        "/givegame — G'oliblarga avtomatik mukofot"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("roles"))
async def cmd_roles(message: Message):
    text = "🎭 **Barcha 32 ta rollar ro'yxati:**\n\n"
    for code, name in ROLES.items():
        text += f"• {name}\n"
    await message.answer(text, parse_mode="Markdown")

# ================= 7. GURUHDA O'YIN BOSHQRUVI =================
@dp.message(Command("game"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_game(message: Message):
    chat_id = message.chat.id
    if chat_id in GAMES and GAMES[chat_id]["status"] == "playing":
        await message.answer("⚠️ Guruhda allaqachon o'yin ketmoqda!")
        return

    GAMES[chat_id] = {
        "status": "waiting",
        "players": {message.from_user.id: message.from_user.first_name},
        "phase": "registration"
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✋ Qo'shilish", callback_data="join_game")
    ]])

    await message.answer(
        f"🎮 **Mafia o'yiniga ro'yxatga olish boshlandi!**\n\n"
        f"👤 Qo'shilganlar (1): {message.from_user.first_name}\n\n"
        f"O'yinni boshlash uchun kamida 4 kishi qo'shilishi va /start yuborilishi kerak.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "join_game")
async def cb_join_game(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    if chat_id not in GAMES or GAMES[chat_id]["status"] != "waiting":
        await call.answer("❌ Hozirda faol ro'yxatdan o'tish yo'q!", show_alert=True)
        return

    if user_id in GAMES[chat_id]["players"]:
        await call.answer("⚠️ Siz allaqachon ro'yxatdasiz!", show_alert=True)
        return

    GAMES[chat_id]["players"][user_id] = user_name
    players_list = "\n".join([f"• {name}" for name in GAMES[chat_id]["players"].values()])

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✋ Qo'shilish", callback_data="join_game")
    ]])

    await call.message.edit_text(
        f"🎮 **Mafia o'yiniga ro'yxatga olish!**\n\n"
        f"👥 **O'yinchilar ({len(GAMES[chat_id]['players'])}):**\n{players_list}\n\n"
        f"Boshlash uchun /start bosing.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await call.answer("✅ O'yinga muvaffaqiyatli qo'shildingiz!")

@dp.message(Command("start"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_start_group(message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES or GAMES[chat_id]["status"] != "waiting":
        await message.answer("⚠️ Avval /game buyrug'i orqali ro'yxatdan o'tishni boshlang!")
        return

    players = GAMES[chat_id]["players"]
    if len(players) < 4:
        await message.answer("❌ O'yinni boshlash uchun kamida 4 ta o'yinchi kerak!")
        return

    GAMES[chat_id]["status"] = "playing"
    assigned_roles = {}
    role_keys = list(ROLES.keys())

    # Rollarni tasodifiy taqsimlash
    for u_id in players:
        r_code = random.choice(role_keys)
        assigned_roles[u_id] = r_code
        try:
            await bot.send_message(u_id, f"🏰 **Sizning rolingiz:** {ROLES[r_code]}")
        except:
            pass

    GAMES[chat_id]["assigned_roles"] = assigned_roles

    await message.answer(
        f"🏙 **Tungi shahar uyquga ketdi...**\n\n"
        f"Barcha o me'yordagi o'yinchilarga rollari shaxsiyga yuborildi!\n"
        f"Tun fazasi boshlandi.",
        parse_mode="Markdown"
    )

@dp.message(Command("stop"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_stop_game(message: Message):
    chat_id = message.chat.id
    if chat_id in GAMES:
        del GAMES[chat_id]
        await message.answer("🛑 O'yin to'xtatildi!")
    else:
        await message.answer("⚠️ Faol o'yin topilmadi.")

# ================= 8. MENYU TUGMALARI HODISALARI =================
@dp.callback_query(F.data == "shaxsiy_kabinet")
async def cb_cabinet(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.first_name)
    vip_status = "👑 VIP A'zo" if u["vip"] else "Oddiy foydalanuvchi"
    text = (
        f"💳 **Shaxsiy Kabinet**\n\n"
        f"👤 Ism: {call.from_user.first_name}\n"
        f"🆔 ID: `{call.from_user.id}`\n"
        f"💰 Tangalar: {u['coins']} ta\n"
        f"💎 Olmoslar: {u['diamonds']} ta\n"
        f"⭐ Status: {vip_status}"
    )
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "daily_bonus")
async def cb_bonus(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.first_name)
    u["coins"] += 200
    u["diamonds"] += 2
    await call.message.answer("🎁 **Kunlik bonus qabul qilindi!**\n\n+200 Tanga 💰\n+2 Olmos 💎", parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "profile")
async def cb_profile(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.first_name)
    text = (
        f"📊 **Statistika va Profil**\n\n"
        f"👤 {call.from_user.first_name}\n"
        f"🎮 Jami o'yinlar: {u['games']}\n"
        f"🏆 G'alabalar: {u['wins']}\n"
        f"💰 Tanga: {u['coins']} | 💎 Olmos: {u['diamonds']}"
    )
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "game_groups")
async def cb_groups(call: CallbackQuery):
    await call.message.answer("🎲 **Rasmiy O'yin Guruhlari:**\n1. @MafiaOfficialChat\n2. @MafiaUzbekistan", parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "rules")
async def cb_rules(call: CallbackQuery):
    text = (
        "📑 **O'yin Qoidalari:**\n\n"
        "1. Tinch aholi va komissar mafiyani topib, ovoz berish orqali yo'q qilishi kerak.\n"
        "2. Mafiya tunda tinch aholini o'ldiradi.\n"
        "3. Shifokor tunda bir kishini davolashi mumkin.\n"
        "4. Kim eng ko'p ovoz topsa, kunduzi shahardan haydaladi."
    )
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "top_players")
async def cb_top(call: CallbackQuery):
    text = "🏆 **Top O'yinchilar:**\n\n1. 👑 Admin — 150 g'alaba\n2. 🔪 ProPlayer — 120 g'alaba\n3. 🕵️ Sherlok — 95 g'alaba"
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

# ================= 9. BOTNI ISHGA TUSHIRISH =================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Pro Mafia Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
