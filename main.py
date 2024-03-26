import wikipedia 
import telebot
import json
import sqlite3
from telebot import types 

wikipedia.set_lang('ru')
bot = telebot.TeleBot('token')

@bot.message_handler(commands=['start'])
def start_func(message):
    with open("users.json", "r") as f_o:
        data_from_json = json.load(f_o)
        user_id = message.from_user.id
        username = message.from_user.username
        if str(user_id) not in data_from_json:
            data_from_json[user_id] = {"username": username}
    with open("users.json", "w") as f_o:
        json.dump(data_from_json, f_o, indent=4, ensure_ascii = False)
    options = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    registration_button = types.KeyboardButton('Регистрация')
    search_button = types.KeyboardButton('Поиск')
    options.add(search_button, registration_button)
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}, я Encyclopedia бот. Что бы вы хотели сделать?", reply_markup=options)

@bot.message_handler(content_types=['text'])
def handle_options(message):
    if message.text == "Поиск":
        bot.send_message(message.chat.id, """*прежде чем начать использовать бота активируйте поиск 
    
Введите запрос для поиска:""")
        bot.register_next_step_handler(message, handle_message)
    elif message.text == "Регистрация":
        registration(message)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    word = message.text
    word = message.text.strip().lower()
    try:
        final_message = wikipedia.summary(word)
    except wikipedia.exceptions.PageError:
        final_message = "Нам не удалось найти вами введённый запрос для поиска"
    bot.send_message(message.chat.id, final_message)

def registration(message):
    connect = sqlite3.connect('database.db')
    crs = connect.cursor()
    
    crs.execute("""CREATE TABLE IF NOT EXISTS users(
                id INT AUTO_INCREMENT,
                login VARCHAR(50),
                password VARCHAR(50),
                PRIMARY KEY(id)
    )""")

    connect.commit()
    crs.close()
    bot.send_message(message.chat.id, 'Уважаемый пользователь для регистрации используйте логин или какой нибудь никнейм для удобного использования. Введите логин!')
    bot.register_next_step_handler(message, login)

def login(message):
    login = message.text.strip()
    bot.send_message(message.chat.id, 'Теперь введите пароль!')
    bot.register_next_step_handler(message, password)

def password(message):
    password = message.text.strip()
    connect = sqlite3.connect('database.db')
    crs = connect.cursor()
    
    crs.execute("INSERT INTO users(login, password) VALUES('%s', '%s')" % (login, password))

    connect.commit()
    crs.close()   
    delete_buttons = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Приятной вам работы, вы успешно зарегистрированы!', reply_markup=delete_buttons)

bot.infinity_polling()
