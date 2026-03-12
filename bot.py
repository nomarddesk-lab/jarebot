import os
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Web Server for Render.com ---
# Render requires an open port to keep the service "alive".
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Gari Bot is active!", 200

def run_flask():
    # Render provides the PORT environment variable; defaults to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Content (Arabic Learning Material) ---

LEARNING_CONTENT = [
    "اسم قناتنا \"جاري\" يعبر عن هدفنا في أن نكون قريبين منكم، تماماً مثل الجار الذي يساعد جاره. نحن لا نكتفي بإعطائك معلومات، بل نسير معك في رحلة \"جاري التعلم\" حتى الاحتراف.\n\nما الذي يميزنا؟\n- التركيز على المحادثة.\n- بث مباشر حي.\n- مجتمع داعم.\n\nهدية البداية: التعليم المباشر مجاني لأول 1000 مشترك!",
    "لماذا تُعدّ اللغة الإنجليزية مفتاح نجاحك في عام ٢٠٢٦؟\n\nفي عالمنا اليوم، لم تعد مجرد مهارة إضافية، بل أصبحت ضرورة أساسية للنمو الشخصي والمهني. تهدف قناة جاري إلى تغيير واقع التلقين من خلال توفير بيئة تعليمية تفاعلية تركز على التطبيق العملي.\n\nفرصة تعليمية مجانية لأول ألف مشترك في القناة.",
    "لماذا لا تكفي تطبيقات اللغة وحدها لتحقيق الطلاقة؟\n\nالسبب بسيط: اللغة ممارسة اجتماعية، وليست مجرد حفظ كلمات. توفر التطبيقات المعلومات، لكنها لا تمنحكم الثقة.\n\nرؤية قناة جاري:\n- تصحيح فوري عبر البث المباشر.\n- معلومات مبسطة.\n- بيئة تفاعلية.\n\nالمقاعد محدودة لأول 1000 مشترك فقط!"
]

QUIZ_DATA = [
    {
        "question": "ما هو الهدف الأساسي من تسمية القناة بـ 'جاري'؟",
        "options": ["أن نكون قريبين كالجيران للمساعدة", "بيع أجهزة إلكترونية", "خدمة توصيل طلبات"],
        "correct": 0
    },
    {
        "question": "ما الذي ينقص تطبيقات اللغة التقليدية حسب رؤية 'جاري'؟",
        "options": ["الألوان الجميلة", "الممارسة الاجتماعية والثقة", "كثرة الكلمات"],
        "correct": 1
    },
    {
        "question": "من هم المستفيدون من دروس البث المباشر المجانية؟",
        "options": ["الجميع دائماً", "لا يوجد دروس مجانية", "أول 1000 مشترك فقط"],
        "correct": 2
    }
]

# --- Bot Logic ---
# In-memory storage for user progress.
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    # Custom Keyboard Menu
    keyboard = [
        ["Start Learning 📖", "Today's Quiz 🧠"],
        ["Pause for Today ✋"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Welcome to the Gari Learning Bot! 🏠\n\n"
        "We are here to walk with you step-by-step toward mastery.\n"
        "Choose an option from the menu below to begin."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "Start Learning 📖":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        # Daily limit check
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("You have finished today's lesson! Come back tomorrow for more. ✨")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day])
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("You've finished all currently available lessons! Stay tuned for more.")

    elif text == "Today's Quiz 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            # Create interactive buttons for answers
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Quiz Question:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("You have completed all available quizzes! Great job.")

    elif text == "Pause for Today ✋":
        await update.message.reply_text("Take a break! We'll be waiting for you tomorrow to continue the journey. ☕")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "Correct answer! ✅\n\n"
    else:
        feedback = "Good try! But that wasn't it.\n\n"
    
    feedback += "Your learning is improving so well, come tomorrow for a new question! 🌟"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    # 1. Start Flask in a background thread for Render's health check
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Retrieve Token from Environment Variables
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable is missing.")
        exit(1)
    
    # 3. Initialize and run the Telegram Bot
    print("Starting Gari Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
