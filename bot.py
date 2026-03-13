import os
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Web Server for Render.com ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Gari Bot is active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Content (Brazilian Portuguese Learning Material) ---

LEARNING_CONTENT = [
    # Day 1: Introduction & The "Gari" Concept
    "O nome do nosso canal 'Gari' reflete nosso objetivo de estarmos próximos de você, exatamente como um vizinho que ajuda o outro. Não apenas entregamos informações; caminhamos com você na jornada 'Aprendizado em Curso' (Gari) até a maestria.\n\nO que nos diferencia?\n- Foco na conversação: Focamos no inglês que você realmente usa no dia a dia.\n- Aulas ao vivo: Sessões interativas para tirar dúvidas e corrigir pronúncia.\n- Comunidade de apoio: Um clube onde todos se ajudam.\n\nPresente de Boas-vindas: As aulas ao vivo serão gratuitas para os primeiros 1.000 inscritos!",
    
    # Day 2: Why English in 2026?
    "Por que o inglês é a chave do seu sucesso em 2026?\n\nNo mundo atual, o inglês não é mais um bônus, é uma necessidade básica para o crescimento pessoal e profissional. É a língua da ciência, dos negócios e da comunicação global.\n\nMuitos estudam por anos sem resultados por falta de interação real. O canal Gari muda essa realidade com um ambiente focado na aplicação prática em vez de apenas teoria.\n\nOportunidade gratuita para os primeiros 1.000 inscritos no canal!",
    
    # Day 3: Apps vs. Real Practice
    "Por que apenas aplicativos de idiomas não são suficientes para a fluência?\n\nVocê já sentiu que entende a gramática no app, mas trava na hora de falar? O motivo é simples: a língua é uma prática social. Apps dão informação, mas não dão a confiança de uma conversa real.\n\nVisão Gari:\n- Correção imediata: Nas lives, corrigimos seus erros na hora.\n- Informação simplificada: Explicamos inglês de forma direta.\n- Ambiente interativo: O aprendizado em grupo elimina a timidez.\n\nVagas limitadas para os primeiros 1.000!"
]

QUIZ_DATA = [
    {
        "question": "Qual é o objetivo principal do nome 'Gari'?",
        "options": ["Estar próximo para ajudar como um vizinho", "Vender eletrônicos", "Um serviço de entrega"],
        "correct": 0
    },
    {
        "question": "O que falta nos aplicativos tradicionais segundo a Gari?",
        "options": ["Cores bonitas", "Prática social e confiança", "Muitas palavras"],
        "correct": 1
    },
    {
        "question": "Quem tem acesso às aulas ao vivo gratuitas?",
        "options": ["Todos para sempre", "Ninguém", "Os primeiros 1.000 inscritos"],
        "correct": 2
    }
]

# --- Bot Logic ---
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    # Menu in Portuguese/English
    keyboard = [
        ["Começar a Aprender 📖", "Quiz de Hoje 🧠"],
        ["Pausar por Hoje ✋"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Bem-vindo ao Gari Learning Bot! 🏠\n\n"
        "Estamos aqui para caminhar com você passo a passo rumo à fluência.\n"
        "Escolha uma opção no menu abaixo para começar."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "Começar a Aprender 📖":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("Você já terminou a lição de hoje! Volte amanhã para mais. ✨")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day])
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("Você terminou todas as lições disponíveis! Fique atento para novidades.")

    elif text == "Quiz de Hoje 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Pergunta do Quiz:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Você completou todos os quizzes disponíveis! Bom trabalho.")

    elif text == "Pausar por Hoje ✋":
        await update.message.reply_text("Descanse um pouco! Estaremos te esperando amanhã para continuar a jornada. ☕")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "Resposta correta! ✅\n\n"
    else:
        feedback = "Boa tentativa! Mas não era essa.\n\n"
    
    feedback += "Seu aprendizado está evoluindo muito bem, volte amanhã para uma nova pergunta! 🌟"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable is missing.")
        exit(1)
    
    print("Starting Gari Bot (Portuguese Version)...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
