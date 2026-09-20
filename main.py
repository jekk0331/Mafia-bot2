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

# ================= 2. BOT SOZLAMALARI VA ADMIN TIZIMI =================
BOT_TOKEN = "8861451228:AAHajj8yFyXyqWYMpNtRtEubkvVm5-wL2_Y"
ADMIN_IDS = [1234567890]  # O'z Telegram ID-ingizni kiriting

bot = Bot(token= "8861451228:AAHajj0yFyXyqWfWpNtNtEubkvVm5-wL2_Y")
dp = Dispatcher(storage=MemoryStorage())

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

# ================= 4. QOIDALAR MATNI =================
RULES_TEXT = """📜 **MAFIA O'YINI QOIDALARI**

🎯 **Maqsad**
O'yinda ikki asosiy jamoa mavjud:
• **Tinch aholi** — barcha mafiyalarni topib, ovoz berish orqali chiqarib yuborishi kerak.
• **Mafiya** — o'z sonini tinch aholi soniga teng yoki undan ko'p holatga keltirishi kerak.

━━━━━━━━━━━━━━
*(To'liq o'yin qoidalari va rollar tavsifi)*"""

# ================= 5. MA'LUMOTLAR BAZASI =================
USERS_DB = {}
GAMES = {}

def get_user(user_id, name="O'yinchi"):
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "name": name,
            "dollars": 198655591,
            "diamonds": 2146565503,
            "vip_days": 996,
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
    return USERS_DB[user_id]

# ================= 6. MENYU TUGMALARI =================
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
        [InlineKeyboardButton(text="🏆 Top o'yinchilar", callback_data="top_players")],
        [InlineKeyboardButton(text="🛠 Admin panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================= 7. SHAXSIY CHAT HANDLERLARI =================
@dp.message(Command("start"), F.chat.type == "private")
async def cmd_start_private(message: Message):
    u = get_user(message.from_user.id, message.from_user.first_name)
    if u["banned"]:
        await message.answer("🚫 Siz botdan bloklangansiz!")
        return
    await message.answer(
        "Salom!\nMen 🏰 **Pro MAFIYA Bot** rasmiy botiman.",
        reply_markup=get_main_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

# 📊 SHAXSIY KABINET
@dp.callback_query(F.data == "shaxsiy_kabinet")
async def cb_shaxsiy(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.first_name)
    sw = u["switches"]
    it = u["items"]
    win_rate = round((u["wins"] / u["games"] * 100), 1) if u["games"] > 0 else 0.0

    text = (
        f"📊 **Sizning statistikangiz**\n\n"
        f"💎 **Premium faol** — {u['vip_days']} kun 22 soat qoldi\n\n"
        f"🎖 **Daraja {u['level']}** — 🏋️ {u['title']}\n"
        f"██████░░░░ {u['xp']}/{u['max_xp']} XP\n\n"
        f"💲 **Dollar:** {u['dollars']}\n"
        f"💎 **Olmos:** {u['diamonds']}\n\n"
        f"🗡 **G'alaba:** {u['wins']} | ❌ **Mag'lubiyat:** {u['losses']} | 🎮 **Jami:** {u['games']} ({win_rate}%)\n\n"
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

# 👖 MENING GEROYIM BO'LIMI (RASMDAGIDEK)
@dp.callback_query(F.data == "geroylar")
async def cb_geroylar(call: CallbackQuery):
    u = get_user(call.from_user.id)
    text = (
        "👖 **Geroylarim (2/2)**\n\n"
        "1. **BOt** — ⭐ 30-daraja ✅ (asosiy)\n"
        "   🛡 0/3  🔫 3/3\n"
        "2. **Nomsiz Geroy** — ⭐ 1-daraja\n"
        "   🛡 0/0  🔫 0/0\n\n"
        "✅ belgisi - hozir jangda ishlatiladigan (asosiy) Geroy."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ BOt", callback_data="select_hero_0")],
        [InlineKeyboardButton(text="👤 Nomsiz Geroy", callback_data="select_hero_1")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="shaxsiy_kabinet")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

# GEROYNI BOSHQARISH VA SOZLAMALARI
@dp.callback_query(F.data.startswith("select_hero_"))
async def cb_select_hero(call: CallbackQuery):
    hero_idx = int(call.data.replace("select_hero_", ""))
    u = get_user(call.from_user.id)
    hero = u["heroes"][hero_idx]

    text = (
        f"👖 **{hero['name']}**\n\n"
        f"⭐ Level: {hero['level']}\n"
        f"✨ XP: {hero['xp']}\n"
        f"❌ Hujum: yo'q (kamida 10-daraja kerak)\n"
        f"❌ Himoya: yo'q (kamida 10-daraja kerak)\n\n"
        f"🛒 **Xaridlar uchun:**\n"
        f"• Himoyani yangilash = 💲 300\n"
        f"• Qurolni zaryadlash = 💲 300\n"
        f"• Geroy nomini o'zgartirish = 💲 2500"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛡 Himoyani to'ldirish", callback_data=f"hero_def_{hero_idx}"),
            InlineKeyboardButton(text="🔋 Zaryadlash", callback_data=f"hero_chg_{hero_idx}")
        ],
        [InlineKeyboardButton(text="⬆️ Darajani ko'tarish", callback_data=f"hero_lvl_{hero_idx}")],
        [
            InlineKeyboardButton(text="✏️ Nomini o'zgartirish", callback_data=f"hero_rename_{hero_idx}"),
            InlineKeyboardButton(text="📊 Darajalar", callback_data="geroy_levels")
        ],
        [InlineKeyboardButton(text="✅ Asosiy (faol) qilish", callback_data=f"hero_set_{hero_idx}")],
        [InlineKeyboardButton(text="🎁 Boshqa o'yinchiga sovg'a qilish", callback_data="hero_gift")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="geroylar")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

# 🛒 DO'KON BO'LIMI (RASMDAGIDEK)
@dp.callback_query(F.data == "dokon")
async def cb_dokon(call: CallbackQuery):
    text = "🛒 **Nima sotib olamiz?**"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Himoya — 💲 140", callback_data="buy_himoya")],
        [InlineKeyboardButton(text="📄 Hujjatlar — 💲 190", callback_data="buy_hujjat")],
        [InlineKeyboardButton(text="⚖️ Ovoz berishni himoya qilish — 💎 1", callback_data="buy_ovoz")],
        [InlineKeyboardButton(text="💔 Qotildan himoya — 💎 2", callback_data="buy_qotil")],
        [InlineKeyboardButton(text="🔫 Qurol — 💎 2", callback_data="buy_qurol")],
        [InlineKeyboardButton(text="🎭 Maska — 💎 2", callback_data="buy_maska")],
        [InlineKeyboardButton(text="🎭 Faol rol — 💎 2", callback_data="buy_rol")],
        [InlineKeyboardButton(text="🔄 Statistikani tiklash — 💲 500", callback_data="buy_stat")],
        [InlineKeyboardButton(text="💎 Premium", callback_data="buy_premium")],
        [InlineKeyboardButton(text="⭐ Stars orqali olmos sotib olish", callback_data="buy_stars")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="shaxsiy_kabinet")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def cb_buy_item(call: CallbackQuery):
    await call.answer("✅ Muvaffaqiyatli xarid qilindi!", show_alert=True)

# 🛠 FULL ADMIN PANEL
def get_full_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Olmos berish", callback_data="adm_give_diamonds"), InlineKeyboardButton(text="Olmos olish", callback_data="adm_take_diamonds")],
        [InlineKeyboardButton(text="⭐ VIP berish", callback_data="adm_give_vip"), InlineKeyboardButton(text="🚫 VIP olish", callback_data="adm_take_vip")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📈 Foydalanuvchilar statistikasi", callback_data="adm_user_stats")],
        [InlineKeyboardButton(text="🌐 Web panel (grafik dashboard)", callback_data="adm_web_panel")],
        [InlineKeyboardButton(text="📡 Bot holati (monitoring)", callback_data="adm_monitoring")],
        [InlineKeyboardButton(text="💰 Daromad statistikasi", callback_data="adm_income_stats")],
        [InlineKeyboardButton(text="⚠️ Manfiy balansli foydalanuvchilar", callback_data="adm_negative_balances")],
        [InlineKeyboardButton(text="📋 Ma'lumot (foydalanuvchi/guruh)", callback_data="adm_info")],
        [InlineKeyboardButton(text="⭐ TOP reyting", callback_data="adm_top_rating")],
        [InlineKeyboardButton(text="📋 Guruhlar ro'yxati", callback_data="adm_groups_list")],
        [InlineKeyboardButton(text="📢 Ommaviy xabar (broadcast)", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🚫 Ban qilish", callback_data="adm_ban"), InlineKeyboardButton(text="✅ Banni olib tashlash", callback_data="adm_unban")],
        [InlineKeyboardButton(text="☠️ Ban + Statistikani tozalash", callback_data="adm_ban_clear")],
        [InlineKeyboardButton(text="⏸ O'yinni to'xtatish", callback_data="adm_stop_game")],
        [InlineKeyboardButton(text="💰 Narxlar (Stars)", callback_data="adm_stars_prices")],
        [InlineKeyboardButton(text="📢 G'olib mukofoti kanali", callback_data="adm_winner_channel")],
        [InlineKeyboardButton(text="📰 Yangiliklar kanali (asosiy menyu)", callback_data="adm_news_channel")],
        [InlineKeyboardButton(text="🔗 Majburiy obuna kanallari", callback_data="adm_sub_channels")],
        [InlineKeyboardButton(text="🎁 Kunlik bonus kanallari", callback_data="adm_bonus_channels")],
        [InlineKeyboardButton(text="🌓 Kun/Tun rasm-video", callback_data="adm_day_night_media")],
        [InlineKeyboardButton(text="🛒 Do'kon narxlari", callback_data="adm_shop_prices")],
        [InlineKeyboardButton(text="🎉 Bonus tarqatish", callback_data="adm_give_bonus")],
        [InlineKeyboardButton(text="🏆 Konkurs", callback_data="adm_contest")],
        [InlineKeyboardButton(text="💎 Pro narxi", callback_data="adm_pro_price")],
        [InlineKeyboardButton(text="🛡 Klanlarni boshqarish", callback_data="adm_manage_clans")],
        [InlineKeyboardButton(text="🎁 Daraja gift'lari (10+)", callback_data="adm_level_gifts")],
        [InlineKeyboardButton(text="🔧 Texnik ishlar", callback_data="adm_maintenance")],
        [InlineKeyboardButton(text="🎨 Rollar premium emoji", callback_data="adm_role_emojis")],
        [InlineKeyboardButton(text="🎨 Mini App menyu emoji", callback_data="adm_miniapp_emojis")],
        [InlineKeyboardButton(text="🔐 Adminlarni boshqarish", callback_data="adm_manage_admins")],
        [InlineKeyboardButton(text="❌ Panelni yopish", callback_data="back_main")]
    ])

@dp.message(Command("admin"))
@dp.callback_query(F.data == "admin_panel")
async def cmd_admin_panel(event):
    text = "🛠 **Admin panel**\n\nKerakli bo'limni tanlang:"
    kb = get_full_admin_keyboard()
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("adm_"))
async def cb_admin_actions(call: CallbackQuery):
    action = call.data.replace("adm_", "")
    await call.answer(f"⚙️ {action.replace('_', ' ').capitalize()} bo'limi tanlandi.", show_alert=True)

# 📑 QOIDALAR VA ORQAGA
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

# ================= 8. GURUHDA O'YIN TIZIMI =================
@dp.message(Command("game"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_game(message: Message):
    chat_id = message.chat.id
    if chat_id in GAMES and GAMES[chat_id]["status"] == "playing":
        await message.answer("⚠️ Guruhda allaqachon o'yin ketmoqda!")
        return
    GAMES[chat_id] = {"status": "waiting", "players": {message.from_user.id: message.from_user.first_name}}
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✋ Qo'shilish", callback_data="join_game")]])
    await message.answer("🎮 **Mafia o'yiniga ro'yxatga olish boshlandi!**\n\nBoshlash uchun /start bosing.", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "join_game")
async def cb_join_game(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    if chat_id in GAMES and GAMES[chat_id]["status"] == "waiting":
        GAMES[chat_id]["players"][user_id] = call.from_user.first_name
        await call.answer("✅ Siz o'yinga qo'shildingiz!")

# ================= 9. ISHGA TUSHIRISH =================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Pro MAFIYA Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
