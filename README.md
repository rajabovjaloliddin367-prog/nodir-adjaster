# 🚗 Yevroprotokol Xorazm — Telegram Bot

Bot: `@nodir_adjaster_bot`

Bot Aiogram 3 asosida yozilgan va Railway'da Docker orqali ishlaydi.

## Bot nima qiladi?

Foydalanuvchi juda oddiy menyu orqali:

- 🚨 YTH bo'yicha murojaat qiladi
- 📄 Yevroprotokol xizmatini tanlaydi
- 🚗 Avtomobil zararini baholatishni so'raydi
- 📋 Hujjatlar bo'yicha maslahat oladi
- 👨‍💼 Inspektor xizmatini tanlaydi
- 📍 YTH joylashuvini yuboradi
- 📱 Telefon raqamini Telegram orqali yuboradi
- 📝 YTH haqida qisqacha ma'lumot yozadi
- 📸 10 tagacha rasm yuboradi

Murojaat tugagach, barcha ma'lumotlar admin Telegram'iga avtomatik keladi.

## 1. Bot token olish

Telegram'da `@BotFather` ga kiring.

`/mybots` → `@nodir_adjaster_bot` → `API Token`

Tokenni nusxa oling.

**Tokenni GitHub yoki ZIP ichiga yozmang.**

## 2. Telegram ID olish

Telegram'da `@userinfobot` yoki boshqa ishonchli Telegram ID botidan o'z numeric ID'ingizni oling.

Masalan:

`123456789`

## 3. Railway'ga joylash

1. Railway → New Project
2. Deploy from GitHub yoki ZIP loyihani GitHub'ga yuklang
3. Variables bo'limiga kiring
4. Quyidagilarni qo'shing:

`BOT_TOKEN=BotFather tokeningiz`

`ADMIN_IDS=123456789`

5. Deploy qiling.

Railway Dockerfile'ni avtomatik aniqlaydi.

## 4. Test

Telegram'da:

`@nodir_adjaster_bot`

→ `/start`

ni bosing.

Keyin test murojaat yuboring.

Admin Telegram'iga quyidagilar keladi:

- murojaat raqami
- ism
- telefon
- tanlangan xizmat
- manzil / Google Maps location
- YTH tavsifi
- Telegram username va ID
- yuborilgan rasmlar

## Admin

`/stats` — jami murojaatlar sonini ko'rsatadi.

## Muhim

Bu bot polling rejimida ishlaydi. Railway uchun alohida domain yoki webhook shart emas.

SQLite ma'lumotlar bazasi ham mavjud. Railway'da doimiy ma'lumot saqlash kerak bo'lsa, keyinchalik Railway Volume yoki PostgreSQL ulash mumkin.

## Loyiha tuzilishi

```text
yevroprotokol_bot/
├── bot.py
├── requirements.txt
├── Dockerfile
├── railway.toml
├── .env.example
├── .gitignore
└── README.md
```
