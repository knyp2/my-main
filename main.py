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
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က Gemini AI နဲ့ ချိတ်ထားတဲ့ Bot ပါ။ စာတွေရော ပုံတွေပါ ပို့ပြီး မေးမြန်းနိုင်ပါတယ် ခဗျာ။")

# စာသား (Text) တွေကို လက်ခံဖြေကြားမယ့် Function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # စဉ်းစားနေကြောင်း Telegram မှာ typing status ပြမယ်
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        # 503 သို့မဟုတ် တခြား Error တက်ရင် ကြင်နာစွာ အကြောင်းပြန်မယ်
        await update.message.reply_text(f"ဆာဗာ ခေတ္တ ဝန်ပိနေပါသည် (သို့) အမှားအယွင်းရှိပါသည်၊ ကျေးဇူးပြု၍ ခဏနေမှ ထပ်ကြိုးစားပေးပါ။ Error: {str(e)}")

# ပုံ (Photo) တွေကို လက်ခံပြီး Gemini ဆီ ပို့မယ့် Function
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ပုံစံအနေနဲ့ စဉ်းစားနေကြောင်း upload_photo status ပြမယ်
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")

        # Telegram ထဲ ပို့လိုက်တဲ့ ပုံတွေထဲက အကြီးဆုံး ပုံကို ယူပါမယ်
        photo_file = await update.message.photo[-1].get_file()
        
        # ပုံကို Server ပေါ် ခေတ္တ Download ဆွဲပါမယ်
        photo_bytes = await photo_file.download_as_bytearray()
        
        # ပုံနဲ့အတူ ပါလာတဲ့ စာသား (Caption) ရှိရင် ယူမယ်၊ မရှိရင် မူလ စာသားသုံးမယ်
        caption = update.message.caption or "ဒီပုံထဲမှာ ဘာတွေပါလဲ ရှင်းပြပေးပါ"

        # Gemini ရဲ့ SDK အသစ်နဲ့ ပုံကို ပို့ပြီး စစ်ဆေးခိုင်းခြင်း
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                caption,
                {
                    "mime_type": "image/jpeg",
                    "data": bytes(photo_bytes)
                }
            ]
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"ပုံကို စစ်ဆေးရာတွင် Error ဖြစ်သွားပါသည် (သို့မဟုတ် ဆာဗာဝန်ပိနေပါသည်): {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers တွေ သတ်မှတ်ခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running with Photo and Typing Status support...")
    app.run_polling()

if __name__ == '__main__':
    main()
