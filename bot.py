import asyncio
import logging
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add BOT_TOKEN in Railway Variables.")
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS is not set. Add your Telegram numeric ID in Railway Variables.")

os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ---------- Database ----------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            service TEXT,
            location TEXT,
            description TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_application(data):
    conn = db()
    cur = conn.execute("""
        INSERT INTO applications
        (telegram_id, username, full_name, phone, service, location, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("telegram_id"),
        data.get("username"),
        data.get("full_name"),
        data.get("phone"),
        data.get("service"),
        data.get("location"),
        data.get("description"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    app_id = cur.lastrowid
    conn.commit()
    conn.close()
    return app_id

def count_applications():
    conn = db()
    n = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return n

# ---------- Keyboards ----------
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚨 YTH SODIR BO'LDI")],
            [KeyboardButton(text="📄 YEVROPROTOKOL"), KeyboardButton(text="🚗 AVTOMOBILNI BAHOLASH")],
            [KeyboardButton(text="📋 HUJJATLAR BO'YICHA MASLAHAT")],
            [KeyboardButton(text="👨‍💼 INSPEKTOR XIZMATI")],
            [KeyboardButton(text="ℹ️ YEVROPROTOKOL NIMA?")],
            [KeyboardButton(text="📞 BOG'LANISH")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ BOSH MENYU")]],
        resize_keyboard=True,
    )

def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)],
            [KeyboardButton(text="⬅️ BOSH MENYU")],
        ],
        resize_keyboard=True,
    )

def location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)],
            [KeyboardButton(text="✍️ Manzilni yozaman")],
            [KeyboardButton(text="⬅️ BOSH MENYU")],
        ],
        resize_keyboard=True,
    )

def photo_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ RASMLAR TAYYOR")],
            [KeyboardButton(text="⏭ RASM YUBORMAYMAN")],
            [KeyboardButton(text="⬅️ BOSH MENYU")],
        ],
        resize_keyboard=True,
    )

def admin_keyboard(app_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📞 Qo'ng'iroq qilish", callback_data=f"call_{app_id}"),
            InlineKeyboardButton(text="💬 Telegram", callback_data=f"tg_{app_id}"),
        ]
    ])

# ---------- FSM ----------
class Application(StatesGroup):
    service = State()
    name = State()
    phone = State()
    location = State()
    description = State()
    photos = State()

SERVICE_MAP = {
    "🚨 YTH SODIR BO'LDI": "YTH bo'yicha shoshilinch yordam",
    "📄 YEVROPROTOKOL": "Yevroprotokol rasmiylashtirish",
    "🚗 AVTOMOBILNI BAHOLASH": "Avtomobil zararini baholash",
    "📋 HUJJATLAR BO'YICHA MASLAHAT": "Hujjatlar bo'yicha maslahat",
    "👨‍💼 INSPEKTOR XIZMATI": "Inspektor xizmati",
}

async def start_message(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "🚗 <b>Nodir Adjaster</b> xizmatiga xush kelibsiz.\n\n"
        "Agar YTH sodir bo'lgan bo'lsa yoki avtomobil zararini baholatish kerak bo'lsa, "
        "sizga yordam beramiz.\n\n"
        "👇 Kerakli xizmatni tanlang:"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await start_message(message, state)

@dp.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await start_message(message, state)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Botdan foydalanish juda oson.</b>\n\n"
        "1️⃣ Kerakli xizmatni tanlang.\n"
        "2️⃣ Ismingizni yozing.\n"
        "3️⃣ Telefon raqamingizni yuboring.\n"
        "4️⃣ YTH joyini yuboring.\n"
        "5️⃣ Holatni qisqacha tushuntiring.\n\n"
        "Shundan keyin mutaxassis siz bilan bog'lanadi.",
        reply_markup=main_menu()
    )

@dp.message(F.text == "⬅️ BOSH MENYU")
async def back_home(message: Message, state: FSMContext):
    await start_message(message, state)

@dp.message(F.text.in_(SERVICE_MAP.keys()))
async def choose_service(message: Message, state: FSMContext):
    service = SERVICE_MAP[message.text]
    await state.update_data(service=service)
    await state.set_state(Application.name)
    await message.answer(
        f"✅ Siz tanladingiz: <b>{service}</b>\n\n"
        "👤 <b>Ismingizni yozing:</b>\n"
        "Masalan: Nodir",
        reply_markup=back_menu()
    )

@dp.message(Application.name)
async def get_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("❗ Iltimos, ismingizni yozing.")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(Application.phone)
    await message.answer(
        "📱 <b>Telefon raqamingizni yuboring.</b>\n\n"
        "Pastdagi tugmani bossangiz, raqamingiz avtomatik yuboriladi.",
        reply_markup=phone_keyboard()
    )

@dp.message(Application.phone, F.contact)
async def get_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await state.set_state(Application.location)
    await message.answer(
        "📍 <b>YTH qayerda sodir bo'ldi?</b>\n\n"
        "Agar hozir YTH joyida bo'lsangiz, <b>Joylashuvni yuborish</b> tugmasini bosing.\n"
        "Yoki manzilni oddiy qilib yozishingiz mumkin.",
        reply_markup=location_keyboard()
    )

@dp.message(Application.phone)
async def get_phone_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("📱 Iltimos, telefon raqamingizni yuboring.", reply_markup=phone_keyboard())
        return
    phone = message.text.strip()
    if len(phone) < 7:
        await message.answer("❗ Telefon raqami noto'g'ri ko'rinmoqda. Qaytadan yuboring.")
        return
    await state.update_data(phone=phone)
    await state.set_state(Application.location)
    await message.answer(
        "📍 <b>YTH qayerda sodir bo'ldi?</b>\n\n"
        "Joylashuvni yuboring yoki manzilni yozing.",
        reply_markup=location_keyboard()
    )

@dp.message(Application.location, F.location)
async def get_location(message: Message, state: FSMContext):
    loc = f"https://maps.google.com/?q={message.location.latitude},{message.location.longitude}"
    await state.update_data(location=loc)
    await state.set_state(Application.description)
    await message.answer(
        "📝 <b>YTH haqida qisqacha yozing.</b>\n\n"
        "Masalan: «Urganch shahrida 2 ta mashina to'qnashdi, mashinamning old qismi shikastlangan.»",
        reply_markup=back_menu()
    )

@dp.message(Application.location, F.text == "✍️ Manzilni yozaman")
async def location_text_start(message: Message, state: FSMContext):
    await message.answer("✍️ Iltimos, YTH bo'lgan manzilni yozing.", reply_markup=back_menu())

@dp.message(Application.location, F.text)
async def get_location_text(message: Message, state: FSMContext):
    if message.text in ("⬅️ BOSH MENYU", "✍️ Manzilni yozaman"):
        return
    await state.update_data(location=message.text.strip())
    await state.set_state(Application.description)
    await message.answer(
        "📝 <b>YTH haqida qisqacha yozing.</b>\n\n"
        "Masalan: «Urganch shahrida 2 ta mashina to'qnashdi.»",
        reply_markup=back_menu()
    )

@dp.message(Application.description)
async def get_description(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❗ Iltimos, holatni qisqacha yozing.")
        return
    await state.update_data(description=message.text.strip(), photos=[])
    await state.set_state(Application.photos)
    await message.answer(
        "📸 <b>YTH yoki avtomobil rasmlari bormi?</b>\n\n"
        "Rasmlar bo'lsa, shu yerga yuboring. Bir nechta rasm yuborishingiz mumkin.\n\n"
        "Rasmlar tugagach <b>«RASMLAR TAYYOR»</b> tugmasini bosing.",
        reply_markup=photo_keyboard()
    )

@dp.message(Application.photos, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 10:
        await message.answer("📸 Maksimal 10 ta rasm qabul qilinadi. «RASMLAR TAYYOR» tugmasini bosing.", reply_markup=photo_keyboard())
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(
        f"✅ Rasm qabul qilindi. ({len(photos)}/10)\nYana rasm yuborishingiz mumkin yoki «RASMLAR TAYYOR» ni bosing.",
        reply_markup=photo_keyboard()
    )

async def finish_application(message: Message, state: FSMContext):
    data = await state.get_data()
    data["telegram_id"] = message.from_user.id
    data["username"] = message.from_user.username or ""
    app_id = save_application(data)

    photos = data.get("photos", [])
    username = f"@{data['username']}" if data["username"] else "username yo'q"
    admin_text = (
        f"🚨 <b>YANGI MUROJAAT #{app_id}</b>\n\n"
        f"👤 <b>Ism:</b> {data.get('full_name')}\n"
        f"📱 <b>Telefon:</b> {data.get('phone')}\n"
        f"🔧 <b>Xizmat:</b> {data.get('service')}\n"
        f"📍 <b>Manzil:</b> {data.get('location')}\n"
        f"📝 <b>YTH:</b> {data.get('description')}\n"
        f"👤 <b>Telegram:</b> {username}\n"
        f"🆔 <b>Telegram ID:</b> <code>{message.from_user.id}</code>\n"
        f"📸 <b>Rasmlar:</b> {len(photos)} ta\n"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=admin_keyboard(app_id))
            for photo_id in photos:
                await bot.send_photo(admin_id, photo_id)
        except Exception as e:
            logger.exception("Admin notification failed for %s: %s", admin_id, e)

    await state.clear()
    await message.answer(
        "✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
        "Ma'lumotlaringiz mutaxassisga yuborildi.\n"
        "Tez orada siz bilan bog'lanishadi.\n\n"
        "📞 <b>+998 87 951 20 00</b>\n"
        "📞 <b>+998 91 858 28 28</b>\n\n"
        "Rahmat!",
        reply_markup=main_menu()
    )

@dp.message(Application.photos, F.text == "✅ RASMLAR TAYYOR")
async def photos_done(message: Message, state: FSMContext):
    await finish_application(message, state)

@dp.message(Application.photos, F.text == "⏭ RASM YUBORMAYMAN")
async def photos_skip(message: Message, state: FSMContext):
    await finish_application(message, state)

@dp.message(F.text == "ℹ️ YEVROPROTOKOL NIMA?")
async def euro_info(message: Message):
    await message.answer(
        "📄 <b>Yevroprotokol nima?</b>\n\n"
        "Yevroprotokol — ayrim kichik yo'l-transport hodisalarini belgilangan tartib va shartlar asosida "
        "rasmiylashtirish uchun ishlatiladigan hujjat.\n\n"
        "Hujjatni to'g'ri to'ldirish va sizning holatingizda qanday tartib amal qilishini bilish uchun "
        "mutaxassis bilan maslahatlashishingiz mumkin.\n\n"
        "👇 Yordam kerak bo'lsa, <b>YEVROPROTOKOL</b> tugmasini bosing.",
        reply_markup=main_menu()
    )

@dp.message(F.text == "📞 BOG'LANISH")
async def contact(message: Message):
    await message.answer(
        "📞 <b>Biz bilan bog'laning</b>\n\n"
        "Asosiy telefon:\n<b>+998 87 951 20 00</b>\n\n"
        "Qo'shimcha telefon:\n<b>+998 91 858 28 28</b>\n\n"
        "Telegram: <b>@Nodir_Adjaster</b>\n\n"
        "Xorazm viloyatida xizmat ko'rsatiladi.",
        reply_markup=main_menu()
    )

@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(f"📊 Jami murojaatlar: <b>{count_applications()}</b> ta.")

@dp.message()
async def fallback(message: Message):
    await message.answer(
        "👇 Iltimos, quyidagi menyudan kerakli xizmatni tanlang.",
        reply_markup=main_menu()
    )

async def main():
    init_db()
    logger.info("Bot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
