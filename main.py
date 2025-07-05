# === नया और स्मार्ट कोड ===

import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# टोकन को Secrets से लेना
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# बातचीत के स्टेप्स (States)
BRAND, MODEL, RAM = range(3)

# सभी फोन मॉडल्स का डेटा (इसे आप और बढ़ा सकते हैं)
phone_models = {
    "Samsung": ["Galaxy S23", "Galaxy A54", "Galaxy M34", "Galaxy F23"],
    "Xiaomi": ["Redmi Note 12 Pro", "Poco F5", "Poco X3 Pro", "Redmi 10"],
    "Realme": ["Realme 11 Pro", "Realme GT Master", "Realme Narzo 50"],
    "Apple": ["iPhone 14 Pro", "iPhone 13", "iPhone 11", "iPhone XR"]
}

# --- बातचीत शुरू करने वाले फंक्शन ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "नमस्ते! मैं आपका एडवांस सेंसिटिविटी बॉट हूँ।\n\n"
        "अपने फोन के लिए बेस्ट सेंसिटिविटी पाने के लिए /sensitivity कमांड का इस्तेमाल करें।"
    )

async def sensitivity_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton(brand, callback_data=brand)] for brand in phone_models.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Step 1: अपना मोबाइल ब्रांड चुनें:", reply_markup=reply_markup)
    return BRAND

# --- ब्रांड चुनने के बाद का फंक्शन ---
async def brand_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    brand = query.data
    context.user_data['brand'] = brand # यूजर का ब्रांड सेव कर लिया
    
    models = phone_models[brand]
    keyboard = [
        [InlineKeyboardButton(model, callback_data=model)] for model in models
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f"Step 2: अब अपना {brand} मॉडल चुनें:", reply_markup=reply_markup)
    return MODEL

# --- मॉडल चुनने के बाद का फंक्शन ---
async def model_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    model = query.data
    context.user_data['model'] = model # यूजर का मॉडल सेव कर लिया

    ram_options = ["4 GB", "6 GB", "8 GB", "12 GB+"]
    keyboard = [
        [InlineKeyboardButton(ram, callback_data=ram)] for ram in ram_options
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text="Step 3: अपनी रैम (RAM) चुनें:", reply_markup=reply_markup)
    return RAM

# --- रैम चुनने के बाद, रिजल्ट दिखाने का फंक्शन ---
async def ram_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    ram = query.data
    brand = context.user_data['brand']
    model = context.user_data['model']
    
    # रैंडम सेंसिटिविटी जेनरेट करें
    general = random.randint(95, 100)
    red_dot = random.randint(92, 100)
    scope_2x = random.randint(88, 98)
    # आप चाहें तो रैम के हिसाब से वैल्यू बदल सकते हैं
    if "4 GB" in ram:
        dpi = random.randint(380, 420)
    else:
        dpi = random.randint(450, 520)

    result_text = (
        f"✅ आपके {brand} {model} ({ram}) के लिए सेंसिटिविटी:\n\n"
        f"🎯 General: {general}\n"
        f"🎯 Red Dot: {red_dot}\n"
        f"🎯 2x Scope: {scope_2x}\n"
        f"🎯 4x Scope: {random.randint(85, 95)}\n"
        f"🎯 Sniper Scope: {random.randint(75, 88)}\n"
        f"🎯 Free Look: {random.randint(70, 90)}\n\n"
        f"✨ (Bonus) DPI: {dpi}\n\n"
        "नई सेंसिटिविटी के लिए दोबारा /sensitivity टाइप करें।"
    )

    await query.edit_message_text(text=result_text)
    return ConversationHandler.END # बातचीत खत्म

# --- बातचीत कैंसिल करने का फंक्शन ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("प्रोसेस कैंसिल कर दिया गया है।")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # बातचीत को संभालने वाला ConversationHandler
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
    
    print("स्मार्ट बॉट अब चल रहा है...")
    application.run_polling()

if __name__ == "__main__":
    main()
