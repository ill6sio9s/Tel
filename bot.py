from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import requests
import asyncio
import urllib.parse
from io import BytesIO

# ================== TOKEN ==================
TOKEN = "8469319200:AAHuOlH4-VddX58ZPBqcz9mypSvZf880fgA"


# ================== AI ==================
GROQ_API_KEY = "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"

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]


def _ask_ai_sync(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    for model in MODELS:
        try:
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "تو یک دستیار هوشمند فارسی هستی."},
                    {"role": "user", "content": prompt}
                ]
            }

            r = requests.post(url, headers=headers, json=data, timeout=30)

            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]

        except Exception:
            continue

    return "❌ هیچ مدل فعالی پاسخ نداد."


async def ask_ai(prompt: str):
    return await asyncio.to_thread(_ask_ai_sync, prompt)


# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["✨ برکت‌های من ✨"],
        ["بازگشت به منوی اصلی"]
    ]

    await update.message.reply_text(
        "منوی اصلی 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ---------- BUTTONS ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("اوکی 👍")


# ---------- CHAT (REPLY ONLY + SAFE IMAGE SYSTEM) ----------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # 🔴 فقط روی ریپلای جواب بده
    if not update.message.reply_to_message:
        return

    # ---------- IMAGE SYSTEM (99% SAFE) ----------
    if text.startswith("عکس "):
        prompt = text.replace("عکس ", "").strip()
        encoded = urllib.parse.quote(prompt)

        # 🟢 AI image source
        url1 = f"https://image.pollinations.ai/prompt/{encoded}"

        try:
            img = requests.get(url1, timeout=20)

            if img.status_code == 200 and len(img.content) > 3000:
                bio = BytesIO(img.content)
                bio.name = "image.png"

                await update.message.reply_photo(
                    photo=bio,
                    caption="🖼️ ساخته شد"
                )
            else:
                raise Exception("AI failed")

        except:
            # 🔵 fallback image (always works)
            try:
                img2 = requests.get("https://picsum.photos/512", timeout=20).content
                bio2 = BytesIO(img2)
                bio2.name = "fallback.png"

                await update.message.reply_photo(
                    photo=bio2,
                    caption="⚠️ AI جواب نداد، تصویر جایگزین ارسال شد"
                )
            except:
                await update.message.reply_text("❌ هیچ تصویری نتونستم بسازم")

        return

    # ---------- AI TEXT ----------
    answer = await ask_ai(text)
    await update.message.reply_text(answer)


# ---------- APP ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
