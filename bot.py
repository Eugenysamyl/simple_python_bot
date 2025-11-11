from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Привет 👋", "Помощь ❓"], ["Весёлое сообщение 😄", "Прощай 👋"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот с кнопками. Выбери действие:", reply_markup=reply_markup
    )

# Ответ на текстовые сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "привет" in text:
        await update.message.reply_text("Привет! Рад тебя видеть 😎")
    elif "помощь" in text:
        await update.message.reply_text("Вот что я умею:\n- Привет 👋\n- Весёлое сообщение 😄\n- Прощай 👋")
    elif "весёлое" in text:
        await update.message.reply_text("😆 Вот тебе шутка: Почему программисты любят кофе? Потому что без него код не компилируется!")
    elif "прощай" in text:
        await update.message.reply_text("Пока! 👋 До скорой встречи!")
    else:
        await update.message.reply_text("Я пока не понимаю это сообщение 🤔")

# Основная функция запуска бота
def main():
    TOKEN = "ВАШ-ТОКЕН"

    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()