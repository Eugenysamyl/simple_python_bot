import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Хранение данных пользователей (в реальном проекте используйте базу данных)
user_data = {}

# Символы для слотов
SLOT_SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']


class CasinoBot:
    def __init__(self):
        self.min_bet = 10
        self.max_bet = 1000

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id

        if user_id not in user_data:
            user_data[user_id] = {
                'balance': 1000,  # Стартовый баланс
                'username': update.effective_user.first_name
            }

        keyboard = [
            [InlineKeyboardButton("🎰 Играть в слоты", callback_data="play_slots")],
            [InlineKeyboardButton("💰 Мой баланс", callback_data="balance")],
            [InlineKeyboardButton("💳 Пополнить баланс", callback_data="deposit")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🎉 Добро пожаловать в казино, {user_data[user_id]['username']}!\n\n"
            f"💰 Ваш баланс: {user_data[user_id]['balance']} монет\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        if data == "play_slots":
            await self.show_slots_menu(query, user_id)
        elif data == "balance":
            await self.show_balance(query, user_id)
        elif data == "deposit":
            await self.show_deposit_menu(query, user_id)
        elif data == "stats":
            await self.show_stats(query, user_id)
        elif data == "help":
            await self.show_help(query)
        elif data.startswith("bet_"):
            bet_amount = int(data.split("_")[1])
            await self.play_slots(query, user_id, bet_amount)
        elif data == "slots_menu":
            await self.show_slots_menu(query, user_id)
        elif data == "main_menu":
            await self.show_main_menu(query, user_id)

    async def show_main_menu(self, query, user_id):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("🎰 Играть в слоты", callback_data="play_slots")],
            [InlineKeyboardButton("💰 Мой баланс", callback_data="balance")],
            [InlineKeyboardButton("💳 Пополнить баланс", callback_data="deposit")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🎯 Главное меню\n\n"
            f"💰 Баланс: {user_data[user_id]['balance']} монет\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )

    async def show_slots_menu(self, query, user_id):
        """Показать меню выбора ставки для слотов"""
        balance = user_data[user_id]['balance']

        # Создаем кнопки со ставками
        bet_buttons = []
        bets = [10, 50, 100, 500]

        for bet in bets:
            if balance >= bet:
                bet_buttons.append(InlineKeyboardButton(f"🎰 {bet} монет", callback_data=f"bet_{bet}"))

        keyboard = [
            bet_buttons,
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🎰 Игровые автоматы\n\n"
            f"💰 Ваш баланс: {balance} монет\n"
            f"📊 Минимальная ставка: {self.min_bet} монет\n"
            f"📈 Максимальная ставка: {self.max_bet} монет\n\n"
            "Выберите ставку:",
            reply_markup=reply_markup
        )

    async def play_slots(self, query, user_id, bet_amount):
        """Игра в слоты"""
        if user_id not in user_data:
            await query.edit_message_text("Ошибка! Начните с команды /start")
            return

        balance = user_data[user_id]['balance']

        # Проверка баланса
        if balance < bet_amount:
            await query.edit_message_text(
                f"❌ Недостаточно средств!\n"
                f"💰 Ваш баланс: {balance} монет\n"
                f"🎰 Требуется: {bet_amount} монет",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Пополнить баланс", callback_data="deposit")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="slots_menu")]
                ])
            )
            return

        # Спин слотов
        slots = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        result = " | ".join(slots)

        # Определение выигрыша
        win_multiplier = 0

        if slots[0] == slots[1] == slots[2]:
            if slots[0] == '7️⃣':
                win_multiplier = 10  # Джекпот
            elif slots[0] == '💎':
                win_multiplier = 5
            elif slots[0] == '🔔':
                win_multiplier = 3
            else:
                win_multiplier = 2
        elif slots[0] == slots[1] or slots[1] == slots[2]:
            win_multiplier = 1  # Маленький выигрыш

        win_amount = bet_amount * win_multiplier

        # Обновление баланса
        user_data[user_id]['balance'] = balance - bet_amount + win_amount

        # Формирование сообщения с результатом
        if win_multiplier > 0:
            if win_multiplier == 10:
                message = f"🎉 ДЖЕКПОТ! 🎉\n\n"
            else:
                message = f"🎉 ВЫ ВЫИГРАЛИ! 🎉\n\n"
            message += f"💰 Выигрыш: {win_amount} монет (x{win_multiplier})\n"
        else:
            message = "😞 Повезет в следующий раз!\n\n"

        message += f"🎰 Результат: {result}\n"
        message += f"💸 Ставка: {bet_amount} монет\n"
        message += f"💰 Новый баланс: {user_data[user_id]['balance']} монет"

        keyboard = [
            [InlineKeyboardButton("🎰 Играть еще", callback_data="play_slots")],
            [InlineKeyboardButton("💰 Мой баланс", callback_data="balance")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    async def show_balance(self, query, user_id):
        """Показать баланс"""
        balance = user_data[user_id]['balance']

        keyboard = [
            [InlineKeyboardButton("💳 Пополнить баланс", callback_data="deposit")],
            [InlineKeyboardButton("🎰 Играть в слоты", callback_data="play_slots")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"💰 Ваш баланс: {balance} монет\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )

    async def show_deposit_menu(self, query, user_id):
        """Показать меню пополнения баланса"""
        keyboard = [
            [InlineKeyboardButton("➕ 100 монет", callback_data="add_100")],
            [InlineKeyboardButton("➕ 500 монет", callback_data="add_500")],
            [InlineKeyboardButton("➕ 1000 монет", callback_data="add_1000")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "💳 Пополнение баланса\n\n"
            "Выберите сумму для пополнения:",
            reply_markup=reply_markup
        )

    async def show_stats(self, query, user_id):
        """Показать статистику"""
        balance = user_data[user_id]['balance']

        keyboard = [
            [InlineKeyboardButton("🎰 Играть в слоты", callback_data="play_slots")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📊 Статистика\n\n"
            f"👤 Игрок: {user_data[user_id]['username']}\n"
            f"💰 Баланс: {balance} монет\n"
            f"🎰 Минимальная ставка: {self.min_bet} монет\n"
            f"📈 Максимальная ставка: {self.max_bet} монет",
            reply_markup=reply_markup
        )

    async def show_help(self, query):
        """Показать справку"""
        help_text = (
            "❓ Помощь по игре\n\n"
            "🎰 Игровые автоматы:\n"
            "• 3 одинаковых символа = выигрыш x2-x10\n"
            "• 2 одинаковых символа = возврат ставки\n"
            "• Разные символы = проигрыш\n\n"
            "💰 Символы и множители:\n"
            "• 7️⃣ x3 = Джекпот x10\n"
            "• 💎 x3 = x5\n"
            "• 🔔 x3 = x3\n"
            "• 🍒🍊🍋🍇 x3 = x2\n\n"
            "💸 Ставки: 10, 50, 100, 500 монет"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(help_text, reply_markup=reply_markup)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        await update.message.reply_text(
            "Используйте кнопки меню для навигации или команду /start"
        )


def main():
    """Запуск бота"""
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    TOKEN = "8471356590:AAHmHT5Ax4T5_kZ5Lzksb56sUt_MtdRfMo4"

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Создаем экземпляр бота
    casino_bot = CasinoBot()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", casino_bot.start))
    application.add_handler(CallbackQueryHandler(casino_bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, casino_bot.handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()