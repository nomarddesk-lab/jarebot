import os
import threading
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- إعدادات خادم الويب لـ Render ---
# Render يتطلب وجود منفذ مفتوح للحفاظ على استمرارية الخدمة
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- محتوى البوت (المقالات والأسئلة) ---

LEARNING_CONTENT = [
    # اليوم الأول
    "اسم قناتنا \"جاري\" يعبر عن هدفنا في أن نكون قريبين منكم، تماماً مثل الجار الذي يساعد جاره. نحن لا نكتفي بإعطائك معلومات، بل نسير معك في رحلة \"جاري التعلم\" حتى الاحتراف.\n\nما الذي يميزنا؟\n- التركيز على المحادثة.\n- بث مباشر حي.\n- مجتمع داعم.\n\nهدية البداية: التعليم المباشر مجاني لأول 1000 مشترك!",
    
    # اليوم الثاني
    "لماذا تُعدّ اللغة الإنجليزية مفتاح نجاحك في عام ٢٠٢٦؟\n\nفي عالمنا اليوم، لم تعد مجرد مهارة إضافية، بل أصبحت ضرورة أساسية للنمو الشخصي والمهني. تهدف قناة جاري إلى تغيير واقع التلقين من خلال توفير بيئة تعليمية تفاعلية تركز على التطبيق العملي.\n\nفرصة تعليمية مجانية لأول ألف مشترك في القناة.",
    
    # اليوم الثالث
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

# --- منطق البوت ---

# تخزين مؤقت للمستخدمين (في الإنتاج يفضل استخدام قاعدة بيانات)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"day": 0, "quiz_day": 0, "last_learned": None}
    
    keyboard = [
        ["ابدأ التعلم 📖", "اختبار اليوم 🧠"],
        ["توقف اليوم ✋"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "مرحباً بك في بوت جاري التعليمي! 🏠\n\n"
        "نحن هنا لنسير معك خطوة بخطوة نحو الاحتراف.\n"
        "اختر من القائمة أدناه للبدء."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {"day": 0, "quiz_day": 0, "last_learned": None}

    if text == "ابدأ التعلم 📖":
        current_day = user_data[user_id]["day"]
        
        # التحقق إذا كان قد تعلم اليوم (بناءً على التاريخ)
        today = datetime.now().date()
        if user_data[user_id]["last_learned"] == today:
            await update.message.reply_text("لقد أتممت درس اليوم بنجاح! عد غداً للحصول على معلومة جديدة. ✨")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day])
            user_data[user_id]["day"] += 1
            user_data[user_id]["last_learned"] = today
        else:
            await update.message.reply_text("لقد أتممت الدورة التعليمية المتوفرة حالياً! انتظر منا كل جديد.")

    elif text == "اختبار اليوم 🧠":
        current_quiz = user_data[user_id]["quiz_day"]
        
        if current_quiz < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz]
            buttons = []
            for idx, opt in enumerate(q["options"]):
                buttons.append([InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")])
            
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"سؤال اليوم:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("لقد أجبت على جميع الاختبارات المتاحة! ممتاز.")

    elif text == "توقف اليوم ✋":
        await update.message.reply_text("ارتح قليلاً، نحن بانتظارك غداً لنكمل الرحلة معاً! ☕")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_data[user_id]["quiz_day"]
    selected_option = int(query.data.split("_")[1])
    
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        response = "إجابة صحيحة! ✅\n\n"
    else:
        response = "محاولة جيدة! الإجابة الصحيحة كانت مسجلة لدينا.\n\n"
    
    response += "تطورك التعليمي يسير بشكل رائع جداً، عد غداً للحصول على أسئلة جديدة! 🌟"
    
    user_data[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=response)

if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل البوت
    # ملاحظة: يجب وضع التوكن الخاص بك في متغيرات البيئة على Render
    TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("Bot is starting...")
    application.run_polling()
