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

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# စာသားတွေ ရှည်လွန်းရင် အပိုင်းခွဲပြီး ပို့မယ့် Helper Function
async def send_long_message(update: Update, text: str):
    max_length = 4000
    if len(text) <= max_length:
        await update.message.reply_text(text)
    else:
        for i in range(0, len(text), max_length):
            await update.message.reply_text(text[i:i + max_length])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က Tiger AI ပါ။ စာတွေရော ပုံတွေပါ ပို့ပြီး မေးမြန်းနိုင်ပါတယ် ခဗျာ။")

# စာသား (Text) များကို ဖြေကြားမယ့် Function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # Tiger thinking... လို့ status ပြမယ်
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message,
        )
        
        # အဖြေရှည်ရင် အပိုင်းခွဲပို့မယ်
        await send_long_message(update, response.text)
    except Exception as e:
        error_str = str(e)
        if "503" in error_str or "UNAVAILABLE" in error_str:
            await update.message.reply_text("ဆာဗာ ခေတ္တ ဝန်ပိနေပါသည် (High Demand)။ ကျေးဇူးပြု၍ ခဏနေမှ ထပ်ပို့ပေးပါ ခဗျာ။")
        else:
            await update.message.reply_text(f"Error ဖြစ်သွားပါသည်: {error_str}")

# ပုံ (Photo) များကို လက်ခံပြီး ဖြေကြားမယ့် Function
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Tiger thinking... လို့ upload status ပြမယ်
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")

        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        caption = update.message.caption or "ဒီပုံထဲမှာ ဘာတွေပါလဲ ရှင်းပြပေးပါ"

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
        
        # အဖြေရှည်ရင် အပိုင်းခွဲပို့မယ်
        await send_long_message(update, response.text)
    except Exception as e:
        error_str = str(e)
        if "503" in error_str or "UNAVAILABLE" in error_str:
            await update.message.reply_text("ဆာဗာ ခေတ္တ ဝန်ပိနေပါသည် (High Demand)။ ပုံကြီးနေလို့ ဖြစ်နိုင်ပါတယ်၊ ခဏနေမှ ထပ်ကြိုးစားပေးပါ ခဗျာ။")
        else:
            await update.message.reply_text(f"ပုံကို စစ်ဆေးရာတွင် Error ဖြစ်သွားပါသည်: {error_str}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Tiger AI Bot is running smoothly...")
    app.run_polling()

if __name__ == '__main__':
    main()
