# === अंतिम और सबसे मज़बूत कोड (Vercel के लिए) ===

import os
import random
import logging
import asyncio
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)

# Logging को सेटअप करें
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# टोकन को Secrets से लेना
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# --- बातचीत के स्टेप्स और फोन डेटा (कोई बदलाव नहीं) ---
BRAND, MODEL, RAM = range(3)
phone_models = {
    "Samsung": ["Galaxy S23", "Galaxy A54", "Galaxy M34", "Galaxy F23"],
    "Xiaomi": ["Redmi Note 12 Pro", "Poco F5", "Poco X3 Pro", "Redmi 10"],
    "Realme": ["Realme 11 Pro", "Realme GT Master", "Realme Narzo 50"],
    "Apple": ["iPhone 14 Pro", "iPhone 13", "iPhone 11", "iPhone XR"],
    "Other": ["Low-End Device", "Mid-Range Device", "High-End Device"]
}

# --- बातचीत के फंक्शन्स (कोई बदलाव नहीं) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "नमस्ते! मैं आपका एडवांस सेंसिटिविटी बॉट हूँ।\n\n"
        "अपने फोन के लिए बेस्ट सेंसिटिविटी पाने के लिए /sensitivity कमांड का इस्तेमाल करें।"
    )

async def sensitivity_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton(brand, callback_data=brand)] for brand in phone_models.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Step 1: अपना मोबाइल ब्रांड चुनें:", reply_markup=reply_markup)
    return BRAND

async def brand_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    brand = query.data
    context.user_data['brand'] = brand
    models = phone_models[brand]
    keyboard = [[InlineKeyboardButton(model, callback_data=model)] for model in models]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Step 2: अब अपना {brand} मॉडल चुनें:", reply_markup=reply_markup)
    return MODEL

async def model_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    model = query.data
    context.user_data['model'] = model
    ram_options = ["2-3 GB", "4 GB", "6 GB", "8 GB", "12 GB+"]
    keyboard = [[InlineKeyboardButton(ram, callback_data=ram)] for ram in ram_options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Step 3: अपनी रैम (RAM) चुनें:", reply_markup=reply_markup)
    return RAM

async def ram_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    ram = query.data
    brand = context.user_data.get('brand', 'N/A')
    model = context.user_data.get('model', 'N/A')
    general = random.randint(95, 100)
    red_dot = random.randint(92, 100)
    scope_2x = random.randint(88, 98)
    if "2-3 GB" in ram: dpi = random.randint(360, 410)
    elif "4 GB" in ram: dpi = random.randint(400, 450)
    else: dpi = random.randint(450, 520)
    result_text = (
        f"✅ आपके {brand} {model} ({ram}) के लिए सेंसिटिविटी:\n\n"
        f"🎯 General: {general}\n🎯 Red Dot: {red_dot}\n🎯 2x Scope: {scope_2x}\n"
        f"🎯 4x Scope: {random.randint(85, 95)}\n🎯 Sniper Scope: {random.randint(75, 88)}\n"
        f"🎯 Free Look: {random.randint(70, 90)}\n\n✨ (Bonus) DPI: {dpi}\n\n"
        "नई सेंसिटिविटी के लिए दोबारा /sensitivity टाइप करें।"
    )
    await query.edit_message_text(text=result_text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("प्रोसेस कैंसिल कर दिया गया है।")
    return ConversationHandler.END


# === Vercel के लिए मुख्य सेटअप ===

# एप्लीकेशन को एक बार बनाएं
if BOT_TOKEN:
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("sensitivity", sensitivity_start)],
        states={
            BRAND: [CallbackQueryHandler(brand_choice)],
            MODEL: [CallbackQueryHandler(model_choice)],
            RAM: [CallbackQueryHandler(ram_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
else:
    logger.error("BOT_TOKEN is not set. The application cannot be initialized.")
    application = None


# Vercel इसी 'handler' क्लास को ढूंढेगा
class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # GET रिक्वेस्ट के लिए एक जवाब, ताकि 501 एरर न आए
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello! This is a Telegram bot. Please interact with it on Telegram.")

    def do_POST(self):
        if application is None:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Bot is not configured. Check BOT_TOKEN.")
            return

        try:
            # रिक्वेस्ट बॉडी से डेटा पढ़ें
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            update_data = json.loads(body.decode('utf-8'))
            
            # टेलीग्राम अपडेट को प्रोसेस करें
            # asyncio.run() का इस्तेमाल करें जो इवेंट लूप को मैनेज करता है
            asyncio.run(self.process_telegram_update(update_data))

            # सफलता का जवाब भेजें
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            logger.error(f"Error processing POST request: {e}", exc_info=True)
            self.send_response(500)
            self.end_headers()

    async def process_telegram_update(self, update_data):
        # यह सुनिश्चित करें कि एप्लीकेशन इनिशियलाइज़ हो चुकी है
        await application.initialize()
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        
