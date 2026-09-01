import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def send_long_message(update: Update, text: str):
    max_length = 4000
    if len(text) <= max_length:
        await update.message.reply_text(text)
    else:
        for i in range(0, len(text), max_length):
            await update.message.reply_text(text[i:i + max_length])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က Tiger AI ပါ။ စာတွေရော ပုံတွေပါ ပို့ပြီး မေးမြန်းနိုင်ပါတယ် ခဗျာ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # ပထမဆုံး စာတန်းကို ပို့မယ်
    sent_message = await update.message.reply_text("🐅 Tiger AI is thinking.")
    
    # အစက်လေးတွေ ပြေးစေမယ့် လိုဂျစ် (Loop ၃ ကြိမ်သာ ပြေးမည် - Telegram Rate Limit မမိစေရန်)
    dots_list = [".", "..", "..."]
    
    try:
        # AI ဆီက အဖြေကို ချက်ချင်း တောင်းမယ့်အစား Background မှာ Thread ခွဲထုတ်မယ်
        # ဒါမှမဟုတ် အစက်လေးတွေကို တစ်ချက်ချင်းစီ အလှည့်ကျပြောင်းပေးမယ်
        for dot in dots_list:
            await asyncio.sleep(0.6)
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=sent_message.message_id,
                    text=f"🐅 Tiger AI is thinking{dot}"
                )
            except Exception:
                pass

        # Gemini ဆီကနေ အဖြေတောင်းခံခြင်း
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message,
        )
        
        if len(response.text) <= 4000:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=sent_message.message_id,
                text=response.text
            )
        else:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sent_message.message_id)
            await send_long_message(update, response.text)

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=sent_message.message_id,
                text="⚠️ API Quota ပြည့်သွားပါပြီ။ ကျေးဇူးပြု၍ ခဏစောင့်ပါ သို့မဟုတ် API Key အသစ် လဲပေးပါ။"
            )
        elif "503" in error_str or "UNAVAILABLE" in error_str:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=sent_message.message_id,
                text="ဆာဗာ ခေတ္တ ဝန်ပိနေပါသည် (High Demand)။ ခဏနေမှ ထပ်ကြိုးစားပေးပါ ခဗျာ။"
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=sent_message.message_id,
                text=f"Error ဖြစ်သွားပါသည်: {error_str}"
            )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Tiger AI Bot with smooth thinking animation is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
