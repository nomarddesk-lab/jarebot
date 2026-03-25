import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Web Server for Render.com ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Niko Redirect Bot is active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Logic ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # The exact text you provided
    welcome_text = (
        "📊 Niko Morales | Trader Profesional\n\n"
        "Análisis y operaciones en Opciones Binarias para traders que desean ejecutar con mayor precisión en el mercado.\n\n"
        "Acceso informativo gratuito.\n\n"
        "@Trader_Niko"
    )
    
    # Creates a button with the link to your channel
    keyboard = [
        [InlineKeyboardButton("Entrar al Canal", url="https://t.me/NikoMoralesTrader")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Sends the message with the button
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

if __name__ == '__main__':
    # Start the web server (needed if you host on Render to keep it awake)
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Get your Telegram bot token from the environment variables
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable is missing.")
        exit(1)
    
    print("Starting Niko Redirect Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Only the /start command is needed now
    application.add_handler(CommandHandler("start", start))
    
    # Run the bot
    application.run_polling()
