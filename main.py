import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys တွေကို Environment Variables ကနေ ယူပါမယ်
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# SDK အသစ်နဲ့ Client ကို ချိတ်ဆက်ခြင်း
client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က Gemini AI နဲ့ ချိတ်ထားတဲ့ Bot ပါ။ ဘာတွေ ကူညီပေးရမလဲ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # SDK အသစ်နဲ့ gemini-2.0-flash Model ကို အသုံးပြုခြင်း
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
