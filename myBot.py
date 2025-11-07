from telegram.ext import Application, CommandHandler


# Функция, которая отвечает на команду /start
async def start(update, context):
    # Отправляем сообщение пользователю
    await update.message.reply_text("Hello, World!")


# Главная функция для запуска бота
def main():
    # Вставьте сюда свой токен
    TOKEN = "7214404831:AAHkjypKjQPyofR8dgg7l7O-eIhKSzR1-OI"

    # Создаем Application
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бот (polling — опрос сообщений)
    application.run_polling()


# Запускаем главную функцию
if __name__ == "__main__":
    main()