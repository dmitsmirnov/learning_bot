
import json  
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler  
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def load_history():  
    try:  
        with open("history.json", "r") as file:  
            return json.load(file)  
    except FileNotFoundError:  
        return {}  

def save_history(history):  
    with open("history.json", "w") as file:  
        json.dump(history, file)

def calculate(num1, num2, operation):  
    try:  
        if operation == "+":  
            return num1 + num2  
        elif operation == "-":  
            return num1 - num2  
        elif operation == "*":  
            return num1 * num2  
        elif operation == "/":  
            if num2 == 0:  
                raise ZeroDivisionError("Деление на ноль!")  
            return num1 / num2  
        else:  
            raise ValueError("Неверная операция!")  
    except ZeroDivisionError as e:  
        return str(e)  
    except ValueError as e:  
        return str(e)  

async def calc(update, context):  
    await update.message.reply_text("Введи первое число.")  
    context.user_data["step"] = "num1"

# Функция, которая отвечает на команду /start
async def start(update, context):
    # Отправляем сообщение пользователю
    await update.message.reply_text("Hello, World from pyCharm")

async def handle_message(update, context):
    # Здесь нужно добавить логику обработки сообщений для калькулятора
    user_input = update.message.text
    user_data = context.user_data
    
    if "step" in user_data:
        step = user_data["step"]
        
        if step == "num1":
            try:
                user_data["num1"] = float(user_input)
                user_data["step"] = "num2"
                await update.message.reply_text("Введи второе число.")
            except ValueError:
                await update.message.reply_text("Пожалуйста, введи корректное число.")
        
        elif step == "num2":
            try:
                user_data["num2"] = float(user_input)
                user_data["step"] = "operation"
                
                inline_keyboard = [
                    [InlineKeyboardButton("+", callback_data="+"), InlineKeyboardButton("-", callback_data="-")],
                    [InlineKeyboardButton("/", callback_data="/"), InlineKeyboardButton("*", callback_data="*")]
                ]
                inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                
                keyboard = [["+", "-"], ["/", "*"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                
                #await update.message.reply_text("Выбери операцию", reply_markup=reply_markup)
                await update.message.reply_text("Выбери операцию", reply_markup=inline_markup)
            except ValueError:
                await update.message.reply_text("Пожалуйста, введи корректное число.")
        
        elif step == "operation":
            num1 = user_data["num1"]
            num2 = user_data["num2"]
            operation = user_input
            
            result = calculate(num1, num2, operation)
            
            # Сохраняем в историю
            history = load_history()
            user_id = str(update.effective_user.id)
            if user_id not in history:
                history[user_id] = []
            
            history[user_id].append(f"{num1} {operation} {num2} = {result}")
            save_history(history)
            
            await update.message.reply_text(f"Результат: {result}")
            
            # Очищаем данные пользователя
            user_data.clear()
    else:
        await update.message.reply_text("Используй /calc для начала вычислений или /start для приветствия.")

async def button(update, context):
    query = update.callback_query
    await query.answer()
    #user_id = str(query.from_user.id)
    user_id = str(update.effective_user.id)
    operation = query.data

    if context.user_data.get("step") == "operation":  
        num1 = context.user_data["num1"]  
        num2 = context.user_data["num2"]  
        result = calculate(num1, num2, operation)  
        
        if isinstance(result, str):  
            await query.edit_message_text(f"Ошибка: {result}")  
        else:  
            await query.edit_message_text(f"Результат: {num1} {operation} {num2} = {result}")  
            history = load_history()  
            #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            #entry = f"{timestamp}: {num1} {operation} {num2} = {result}" 
            entry = f"{num1} {operation} {num2} = {result}"  
            if user_id not in history:
                history[user_id] = []  
            history[user_id].append(entry)  
            save_history(history)  
        
        
    elif context.user_data.get("step") == "clear":
        await query.edit_message_text("History is cleard")
        save_history({})

    context.user_data["step"] = None


async def history(update, context):
    user_id = str(update.message.from_user.id)
    data = load_history()
    context.user_data["step"] = "clear"
    if user_id in data and data[user_id]:
        last_five = data[user_id][-5:]
        response = "Last notes: \n" + "\n".join(last_five)
        await update.message.reply_text(response)

        inline_keyboard = [[InlineKeyboardButton("Refresh history", callback_data="clear")]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        await update.message.reply_text("OR", reply_markup=inline_markup)

    else:
        await update.message.reply_text("History is empty")

# Главная функция для запуска бота
def main():
    # Вставьте сюда свой токен
    TOKEN = "7214404831:AAHkjypKjQPyofR8dgg7l7O-eIhKSzR1-OI"

    # Создаем Application
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("calc", calc))  
    application.add_handler(CommandHandler("history", history))  
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    

    # Запускаем бот (polling — опрос сообщений)
    application.run_polling()


# Запускаем главную функцию
if __name__ == "__main__":
    main()
