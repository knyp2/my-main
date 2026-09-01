import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys တွေကို Environment Variables ကနေ ယူပါမယ်
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini ကို Configure လုပ်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က Gemini AI နဲ့ ချိတ်ထားတဲ့ Bot ပါ။ ဘာတွေ ကူညီပေးရမလဲ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # Gemini ဆီကို စာပို့ပြီး အဖြေတောင်းခြင်း
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
    except Exception as e:
        # ဘာ Error တက်နေလဲဆိုတာ တိတိကျကျ သိရအောင် ပြပါမယ်
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands နဲ့ Messages များကို Handlers လုပ်ခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
