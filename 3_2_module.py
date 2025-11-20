
import json  
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler  
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import requests

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
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    #print(response.json())
    await update.message.reply_text("Hello")

async def handle_message(update, context):
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
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                
                await update.message.reply_text("Выбери операцию", reply_markup=reply_markup)
            except ValueError:
                await update.message.reply_text("Пожалуйста, введи корректное число.")
        
        elif step == "operation":
            # Этот блок не должен выполняться при inline кнопках!
            # Он выполняется только если пользователь вводит операцию текстом
            num1 = user_data["num1"]
            num2 = user_data["num2"]
            operation = user_input
            
            result = calculate(num1, num2, operation)
            
            history = load_history()
            user_id = str(update.effective_user.id)
            if user_id not in history:
                history[user_id] = []
            
            history[user_id].append(f"{num1} {operation} {num2} = {result}")
            save_history(history)
            
            
    else:
        await update.message.reply_text("Используй /calc для начала вычислений или /start для приветствия.")

async def button(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    operation = query.data

    #print(f"DEBUG: operation={operation}, step={context.user_data.get('step')}")  # Для отладки

    if operation in ["+", "-", "*", "/"]:  # Если это математическая операция
        if "num1" in context.user_data and "num2" in context.user_data:  
            num1 = context.user_data["num1"]  
            num2 = context.user_data["num2"]  
            result = calculate(num1, num2, operation)  
            
            context.user_data["result"] = result

            if isinstance(result, str):  
                await query.edit_message_text(f"Ошибка: {result}")  
            else:  
                history = load_history()  
                entry = f"{num1} {operation} {num2} = {result}"  
                if user_id not in history:
                    history[user_id] = []  
                history[user_id].append(entry)  
                save_history(history)

                inline_keyboard = [
                    [InlineKeyboardButton("Повторить", callback_data="repeat"),
                     InlineKeyboardButton("В валюте", callback_data="change")]
                ]
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                await query.edit_message_text(
                    f"Результат: {num1} {operation} {num2} = {result}", 
                    reply_markup=reply_markup
                )
   
    elif operation == "clear":
        # Очистка истории
        history = load_history()
        history[user_id] = []
        save_history(history)
        await query.edit_message_text("История очищена")
        
    elif operation == "repeat":
        # Начинаем новый расчет
        context.user_data.clear()  # Очищаем все данные
        context.user_data["step"] = "num1"
        await query.edit_message_text("Введите первое число снова:")
    
    elif operation == "change":
        rates = get_exchange_rate()
        context.user_data["rates"] = rates
        #result = context.user_data.get("result")
        #rub = result * rates["RUB"]
        #history = load_history()
        #history[user_id]["RUB"] = rub
        #save_history(history)
        #await query.edit_message_text(f"Current usd: {rub}")
        #inline_keyboard = [
        #    [InlineKeyboardButton("USD", callback_data="USD"),
        #    InlineKeyboardButton("EUR", callback_data="EUR"),
        #    InlineKeyboardButton("RUB", callback_data="RUB")]
        #]
        inline_keyboard = [[]]
        for i in list(rates)[:10]:
            inline_keyboard.append([InlineKeyboardButton(i,callback_data=i)])


        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await query.edit_message_text(
                    "Select:", 
                    reply_markup=reply_markup
        )
    elif operation in context.user_data.get("rates") :
        rates = context.user_data.get("rates")
        result = context.user_data.get("result")
        cur = result * rates[operation]   
        await query.edit_message_text(f"Current {result} usd: {cur} {operation}") 
        history = load_history()
        history[user_id]



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

def get_exchange_rate():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        response.raise_for_status()
        data = response.json()
        return data["rates"]
    except requests.RequestException as e:
        return None

async def rate(update, context):
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        response.raise_for_status()
        data = response.json()
        usd_eur = data["rates"]["EUR"]
        usd_rub = data["rates"]["RUB"]
        await update.message.reply_text(f"EUR: {usd_eur} and RUB: {usd_rub}")
    except requests.RequestException as e:
        await update.message.reply_text(f"Error {e}")

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
    application.add_handler(CommandHandler("rate", rate))  
 
    

    # Запускаем бот (polling — опрос сообщений)
    application.run_polling()


# Запускаем главную функцию
if __name__ == "__main__":
    main()
