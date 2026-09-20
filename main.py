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
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ================= 1. RENDER PORT SERVERI (24/7 LIVE) =================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Pro MAFIYA Bot 24/7 Live!")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# ================= 2. BOT SOZLAMALARI VA XAVFSIZ ADMIN TIZIMI =================
BOT_TOKEN = "8861451228:AAHajj8yFyXyqWYMpNtRtEubkvVm5-wL2_Y"

# ⚠️ O'zingizning Telegram ID-ingizni shu yerga yozing! (Faqat siz va qo'shilgan adminlar ocha oladi)
ADMIN_IDS = [7486124163] 

bot = Bot(token= "8861451228:AAHajj0yFyXyqWfWpNtNtEubkvVm5-wL2_Y")
dp = Dispatcher(storage=MemoryStorage())

# FSM Holatlari (Admin amallari uchun)
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_give_diamonds = State()
    waiting_for_new_admin = State()

# ================= 3. BARCHA 32 TA ROLLAR =================
ROLES = {
    "tinch": "👨‍🌾 Tinch aholi", "komissar": "🕵️‍♂️ Komissar", "doktor": "👨‍⚕️ Shifokor",
    "serjant": "👮‍♂️ Serjant", "mantiqchi": "🧠 Mantiqchi", "lover": "💃 Ajoyib qiz",
    "detektiv": "🔎 Detektiv", "hamshira": "👩‍⚕️ Hamshira", "aygoqchi": "🕵️ Ayg'oqchi",
    "suvchi": "🌊 Suvchi", "ot_ochiruvchi": "👨‍🚒 O't o'chiruvchi", "qutqaruvchi": "🛟 Qutqaruvchi",
    "xaker": "💻 Xaker", "mer": "🎩 Mer", "mafia": "🕶 Mafiya", "don": "👑 Mafiya Doni", 
    "qotil": "🔪 Qotil", "advokat": "💼 Advokat", "shapoklyak": "👵 Shapoklyak", 
    "qora_beva": "🕷 Qora beva", "snayper": "🎯 Snayper", "terrorchi": "💣 Terrorchi", 
    "ninja": "🥷 Ninja", "ogri": "🦹 O'g'ri", "yollanma": "🏹 Yollanma qotil",
    "kamikadze": "💥 Kamikadze", "maniak": "🪓 Maniak", "joker": "🃏 Joker",
    "psix": "🧪 Psixopat", "aleks": "🌀 Amneziya", "klon": "🪞 Klon", "ozga_sayyoralik": "👽 O'zga sayyoralik"
}

RULES_TEXT = (
    "📜 **MAFIA O'YINI QOIDALARI**\n\n"
    "🎯 **Maqsad:** Tinch aholi barcha mafiyalarni topishi, mafiya esa aholini yo'q qilishi kerak.\n"
    "• **Komissar:** Tunda o'yinchilarni tekshiradi.\n"
    "• **Doktor:** O'yinchilarni davolaydi.\n"
    "• **Don & Mafiya:** Tunda qurbon tanlaydi."
)

# ================= 4. BAZA VA SOZLAMALAR =================
USERS_DB = {}
GAMES = {}
SETTINGS = {
    "required_channels": ["@ProMafiaChannel"],
    "bonus_diamonds": 5
}

def get_user(user_id, name="O'yinchi", username=""):
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "name": name,
            "username": username.lstrip("@"),
            "dollars": 5000,
            "diamonds": 100,
            "vip_days": 30,
            "level": 2,
            "title": "Yangi",
            "xp": 183,
            "max_xp": 300,
            "wins": 2,
            "losses": 5,
            "games": 7,
            "banned": False,
            "heroes": [
                {"name": "BOt", "level": 30, "active": True, "xp": 183},
                {"name": "Nomsiz Geroy", "level": 1, "active": False, "xp": 333}
            ],
            "items": {
                "himoya": 15, "qotil_himoya": 7, "ovoz_himoya": 12,
                "hujjat": 14, "miltiq": 10, "maska": 6, "rol_ehtimol": 0
            },
            "switches": {
                "hujjat": True, "himoya": True, "maska": True,
                "qotil_himoya": True, "ovoz_himoya": True, "miltiq": True
            }
        }
    elif username and not USERS_DB[user_id].get("username"):
        USERS_DB[user_id]["username"] = username.lstrip("@")
    return USERS_DB[user_id]

# ================= 5. ASOSIY MENYU =================
def get_main_keyboard(user_id):
    kb = [
        [InlineKeyboardButton(text="💳 Shaxsiy kabinet", callback_data="shaxsiy_kabinet")],
        [
            InlineKeyboardButton(text="🤖 Botni guruhga qo'sh➕", url="https://t.me/ProMafiaBot?startgroup=true"),
            InlineKeyboardButton(text="👁 Yangiliklar", url="https://t.me/telegram")
        ],
        [InlineKeyboardButton(text="🎲 O'yin guruhlari", callback_data="game_groups")],
        [InlineKeyboardButton(text="🎁 Kunlik bonus", callback_data="daily_bonus")],
        [
            InlineKeyboardButton(text="💳 Profilim", callback_data="shaxsiy_kabinet"),
            InlineKeyboardButton(text="📑 O'yin qoidalari", callback_data="rules")
        ],
        [InlineKeyboardButton(text="🏆 Top o'yinchilar", callback_data="top_players")]
    ]
    if user_id in ADMIN_IDS:
        kb.append([InlineKeyboardButton(text="🛠 Admin panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"), F.chat.type == "private")
async def cmd_start_private(message: Message):
    u = get_user(message.from_user.id, message.from_user.first_name, message.from_user.username or "")
    if u["banned"]:
        await message.answer("🚫 Siz botdan bloklangansiz!")
        return
    await message.answer(
        "Salom!\nMen 🏰 **Pro MAFIYA Bot** rasmiy botiman.",
        reply_markup=get_main_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

# ================= 6. SHAXSIY KABINET VA TOGGLE TUGMALAR =================
@dp.callback_query(F.data == "shaxsiy_kabinet")
async def cb_shaxsiy(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.first_name, call.from_user.username or "")
    sw = u["switches"]
    it = u["items"]
    win_rate = round((u["wins"] / u["games"] * 100), 1) if u["games"] > 0 else 0.0

    text = (
        f"📊 **Sizning statistikangiz**\n\n"
        f"💎 **Premium faol** — {u['vip_days']} kun qoldi\n"
        f"🎖 **Daraja {u['level']}** — 🏋️ {u['title']}\n"
        f"💲 **Dollar:** {u['dollars']} | 💎 **Olmos:** {u['diamonds']}\n"
        f"🗡 G'alaba: {u['wins']} | ❌ Mag'lubiyat: {u['losses']} ({win_rate}%)\n\n"
        f"🛡 Himoya: {it['himoya']} | 💔 Qotildan: {it['qotil_himoya']}\n"
        f"⚖️ Ovoz: {it['ovoz_himoya']} | 📄 Hujjat: {it['hujjat']}\n"
        f"🔫 Qurol: {it['miltiq']} | 🎭 Maska: {it['maska']}"
    )

    def status_btn(key, label):
        status = "🟢 ON" if sw[key] else "🔴 OFF"
        return InlineKeyboardButton(text=f"{label} - {status}", callback_data=f"toggle_{key}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Shaxsiy kabinet", callback_data="shaxsiy_kabinet")],
        [status_btn("hujjat", "📄 Hujjat"), status_btn("himoya", "🛡 Himoya")],
        [status_btn("maska", "🎭 Maska"), status_btn("qotil_himoya", "💔 Qotildan himoya")],
        [status_btn("ovoz_himoya", "⚖️ Ovoz himoya"), status_btn("miltiq", "🔫 Miltiq")],
        [
            InlineKeyboardButton(text="🥇 Yutuqlarim", callback_data="yutuqlar"),
            InlineKeyboardButton(text="🎁 Sovg'alarim tarixi", callback_data="sovgalar")
        ],
        [InlineKeyboardButton(text="👖 Mening Geroyim", callback_data="geroylar")],
        [
            InlineKeyboardButton(text="🛒 Do'kon", callback_data="dokon"),
            InlineKeyboardButton(text="💎 Olmos o'tkazish", callback_data="send_diamonds")
        ],
        [
            InlineKeyboardButton(text="💲 Pul o'tkazish", callback_data="send_money"),
            InlineKeyboardButton(text="💱 Valyuta almashtirish", callback_data="exchange")
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")]
    ])

    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data.startswith("toggle_"))
async def cb_toggle(call: CallbackQuery):
    key = call.data.replace("toggle_", "")
    u = get_user(call.from_user.id)
    if key in u["switches"]:
        u["switches"][key] = not u["switches"][key]
    await cb_shaxsiy(call)

# ================= 7. GEROYLAR VA DO'KON TIZIMI =================
@dp.callback_query(F.data == "geroylar")
async def cb_geroylar(call: CallbackQuery):
    text = (
        "👖 **Geroylarim (2/2)**\n\n"
        "1. **BOt** — ⭐ 30-daraja ✅ (asosiy)\n   🛡 0/3  🔫 3/3\n"
        "2. **Nomsiz Geroy** — ⭐ 1-daraja\n   🛡 0/0  🔫 0/0\n\n"
        "✅ belgisi - hozir jangda ishlatiladigan Geroy."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ BOt", callback_data="select_hero_0")],
        [InlineKeyboardButton(text="👤 Nomsiz Geroy", callback_data="select_hero_1")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="shaxsiy_kabinet")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "dokon")
async def cb_dokon(call: CallbackQuery):
    u = get_user(call.from_user.id)
    text = f"🛒 **Do'kon**\n\n💲 Dollar: {u['dollars']}\n💎 Olmos: {u['diamonds']}\n\nKerakli buyumni tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Himoya — 💲 140", callback_data="shop_himoya")],
        [InlineKeyboardButton(text="📄 Hujjatlar — 💲 190", callback_data="shop_hujjat")],
        [InlineKeyboardButton(text="⚖️ Ovoz himoyasi — 💎 1", callback_data="shop_ovoz")],
        [InlineKeyboardButton(text="💔 Qotildan himoya — 💎 2", callback_data="shop_qotil")],
        [InlineKeyboardButton(text="🔫 Qurol — 💎 2", callback_data="shop_qurol")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="shaxsiy_kabinet")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data.startswith("shop_"))
async def cb_shop_buy(call: CallbackQuery):
    item = call.data.replace("shop_", "")
    u = get_user(call.from_user.id)
    prices_dollar = {"himoya": 140, "hujjat": 190}
    prices_diamond = {"ovoz": 1, "qotil": 2, "qurol": 2}

    if item in prices_dollar:
        cost = prices_dollar[item]
        if u["dollars"] >= cost:
            u["dollars"] -= cost
            u["items"][item] = u["items"].get(item, 0) + 1
            await call.answer(f"✅ Muvaffaqiyatli sotib olindi!", show_alert=True)
        else:
            await call.answer(f"❌ Dollar yetarli emas! Kerak: {cost}", show_alert=True)
    elif item in prices_diamond:
        cost = prices_diamond[item]
        if u["diamonds"] >= cost:
            u["diamonds"] -= cost
            await call.answer(f"✅ Olmos evaziga sotib olindi!", show_alert=True)
        else:
            await call.answer(f"❌ Olmos yetarli emas! Kerak: {cost}", show_alert=True)
    await cb_dokon(call)

# ================= 8. KUNLIK BONUS VA MAJBURIY OBUNA =================
@dp.callback_query(F.data == "daily_bonus")
async def cb_daily_bonus(call: CallbackQuery):
    channels_text = "\n".join([f"• {ch}" for ch in SETTINGS["required_channels"]])
    text = (
        f"🎁 **Kunlik bonus**\n\n"
        f"Quyidagi kanallarga obuna bo'lib, {SETTINGS['bonus_diamonds']} 💎 olmos yutib oling!\n\n"
        f"{channels_text}\n\n"
        f"Obuna bo'lgach, \"✅ Tekshirish\" tugmasini bosing."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_bonus")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "check_bonus")
async def cb_check_bonus(call: CallbackQuery):
    user_id = call.from_user.id
    subscribed = True
    for channel in SETTINGS["required_channels"]:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                subscribed = False
        except Exception:
            pass

    if subscribed:
        u = get_user(user_id)
        u["diamonds"] += SETTINGS["bonus_diamonds"]
        await call.answer(f"✅ Obuna tasdiqlandi! +{SETTINGS['bonus_diamonds']} 💎 Olmos berildi!", show_alert=True)
        await cb_back_main(call)
    else:
        await call.answer("❌ Siz hamma kanallarga obuna bo'lmabsiz!", show_alert=True)

# ================= 9. TOP O'YINCHILAR VA RANDOM SOVG'A =================
@dp.callback_query(F.data == "top_players")
async def cb_top_players(call: CallbackQuery):
    text = "🏆 **Top o'yinchilar**\n\nBo'limni tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 TOP g'oliblar", callback_data="top_winners_menu")],
        [InlineKeyboardButton(text="🎰 Random sovg'a", callback_data="random_gift")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "random_gift")
async def cb_random_gift(call: CallbackQuery):
    u = get_user(call.from_user.id)
    text = (
        "🎰 **Random sovg'a o'yini**\n\n"
        "• Har o'yin uchun 💎 **5 olmos** to'lanadi.\n"
        f"💰 Balansingiz: 💎 {u['diamonds']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 O'ynash (💎 5)", callback_data="play_random_gift")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="top_players")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "play_random_gift")
async def cb_play_gift(call: CallbackQuery):
    u = get_user(call.from_user.id)
    if u["diamonds"] < 5:
        await call.answer("❌ Olmosingiz yetarli emas!", show_alert=True)
        return
    u["diamonds"] -= 5
    prizes = ["🛡 Himoya (+1)", "🔫 Qurol (+1)", "💎 15 Olmos"]
    won = random.choice(prizes)
    await call.answer(f"🎉 Tabriklaymiz! Siz yutdingiz: {won}", show_alert=True)
    await cb_random_gift(call)

# ================= 10. XAVFSIZ ADMIN PANEL & ADMIN QO'SHISH =================
def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Olmos berish", callback_data="adm_give_diamonds")],
        [InlineKeyboardButton(text="🔐 Admin qo'shish", callback_data="adm_add_admin")],
        [InlineKeyboardButton(text="📢 Ommaviy xabar (Broadcast)", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="❌ Panelni yopish", callback_data="back_main")]
    ])

@dp.message(Command("admin"))
@dp.callback_query(F.data == "admin_panel")
async def cmd_admin_panel(event):
    user_id = event.from_user.id
    if user_id not in ADMIN_IDS:
        if isinstance(event, CallbackQuery):
            await event.answer("❌ Kechirasiz, siz admin emassiz!", show_alert=True)
        else:
            await event.answer("❌ Bu buyruq faqat bot adminlari uchun!")
        return

    text = "🛠 **Admin panel**\n\nKerakli bo'limni tanlang:"
    kb = get_admin_keyboard()
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("❌ Ruxsat yo'q!", show_alert=True)
    await call.answer(f"📊 Jami foydalanuvchilar: {len(USERS_DB)} ta\n👑 Adminlar soni: {len(ADMIN_IDS)} ta", show_alert=True)

# Olmos berish
@dp.callback_query(F.data == "adm_give_diamonds")
async def adm_give_diag(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("❌ Ruxsat yo'q!", show_alert=True)
    await call.message.answer("💎 Olmos berish uchun yuboring:\n`@username miqdor`", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_give_diamonds)
    await call.answer()

@dp.message(AdminStates.waiting_for_give_diamonds, F.chat.type == "private")
async def process_give_diag(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        return await message.answer("⚠️ Xato format! Masalan: `@username 50`")
    
    target = parts[0].lstrip("@")
    try:
        amount = int(parts[1])
    except ValueError:
        return await message.answer("⚠️ Miqdor son bo'lishi kerak!")

    found = False
    for uid, udata in USERS_DB.items():
        if udata.get("username", "").lower() == target.lower():
            udata["diamonds"] += amount
            found = True
            await message.answer(f"✅ @{target} ga {amount} 💎 olmos qo'shildi!")
            try:
                await bot.send_message(uid, f"🎁 Admin tomonidan sizga {amount} 💎 olmos berildi!")
            except:
                pass
            break
    if not found:
        await message.answer("❌ Foydalanuvchi bazadan topilmadi!")
    await state.clear()

# --- YANGI: ADMIN QO'SHISH ---
@dp.callback_query(F.data == "adm_add_admin")
async def adm_add_admin_start(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("❌ Ruxsat yo'q!", show_alert=True)
    await call.message.answer(
        "🔐 **Yangi admin qo'shish:**\n\n"
        "Foydalanuvchining **Telegram ID si** yoki **username** ini yuboring (masalan: `123456789` yoki `@username`):",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_new_admin)
    await call.answer()

@dp.message(AdminStates.waiting_for_new_admin, F.chat.type == "private")
async def process_add_admin(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = message.text.strip()
    target_uid = None
    
    if text.isdigit():
        target_uid = int(text)
    else:
        username_clean = text.lstrip("@").lower()
        for uid, udata in USERS_DB.items():
            if udata.get("username", "").lower() == username_clean:
                target_uid = uid
                break
    
    if target_uid:
        if target_uid not in ADMIN_IDS:
            ADMIN_IDS.append(target_uid)
            await message.answer(f"✅ Muvaffaqiyatli! ID: `{target_uid}` botga admin etib tayinlandi.", parse_mode="Markdown")
            try:
                await bot.send_message(target_uid, "👑 Tabriklaymiz! Siz botga **Admin** etib tayinlandingiz. /admin buyrug'i yoki panel orqali boshqarishingiz mumkin.")
            except:
                pass
        else:
            await message.answer("⚠️ Bu foydalanuvchi allaqachon admin!")
    else:
        if text.isdigit():
            target_uid = int(text)
            if target_uid not in ADMIN_IDS:
                ADMIN_IDS.append(target_uid)
                await message.answer(f"✅ ID: `{target_uid}` adminlar ro'yxatiga qo'shildi.", parse_mode="Markdown")
            else:
                await message.answer("⚠️ Bu ID allaqachon admin.")
        else:
            await message.answer("❌ Foydalanuvchi topilmadi! (Foydalanuvchi avval botga /start bosgan bo'lishi shart yoki uning raqamli ID sini kiriting).")
    
    await state.clear()

# Broadcast (Ommaviy xabar)
@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("❌ Ruxsat yo'q!", show_alert=True)
    await call.message.answer("📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni kiriting:")
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.answer()

@dp.message(AdminStates.waiting_for_broadcast, F.chat.type == "private")
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    count = 0
    for uid in USERS_DB:
        try:
            await bot.send_message(uid, message.text)
            count += 1
        except:
            pass
    await message.answer(f"✅ Xabar {count} ta foydalanuvchiga yuborildi!")
    await state.clear()

# ================= 11. UMUMIY QOIDALAR VA ORQAGA =================
@dp.message(Command("rules"))
@dp.callback_query(F.data == "rules")
async def cb_rules(event):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")]])
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(RULES_TEXT, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(RULES_TEXT, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "back_main")
async def cb_back_main(call: CallbackQuery):
    await call.message.edit_text(
        "Salom!\nMen 🏰 **Pro MAFIYA Bot** rasmiy botiman.",
        reply_markup=get_main_keyboard(call.from_user.id),
        parse_mode="Markdown"
    )
    await call.answer()

# ================= 12. ISHGA TUSHIRISH =================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Pro MAFIYA Bot to'liq ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
