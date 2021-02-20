#  - "- coding: utf- 8 - "-
import telebot
from telebot import types
import sqlite3
import control, bd, config
import threading


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет\nНу что, начнем работу?')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB5clgMMy15Mqa1XhwvGMCFt8YWZBAVAACJwADTlzSKVNP23ucCOn1HgQ')
    bd.create_db(message)
    control.menu(bot, message)
    thread = threading.Thread(target=control.check_time, args=(bot, message)) 
    thread.start() 

@bot.message_handler(commands=['menu'])
def menu(message):
    control.menu(bot, message)


@bot.message_handler(content_types=["text"])
def analyze(message):
    if message.text.strip().lower() == "изменить размер долга":
        control.in_data(bot, message)
    elif message.text.strip().lower() == "инфо":
        control.info(bot, message)
    elif message.text.strip().lower() == "изменить км или страховку":
        control.in_km_ins(bot, message)
    elif message.text.strip().lower() == "посадить водителя":
        control.driver_to_car(bot, message)    
    elif message.text.strip().lower() == "добавить машину":
        control.car(bot, message)
    elif message.text.strip().lower() == "добавить водителя":
        control.driver(bot, message)
    elif message.text.strip().lower() == "удалить":
        control.delete(bot, message)
    else:
        bot.send_message(message.chat.id, "Ваш запрос непонятен,\nвведите запрос еще раз")
        control.menu(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data.startswith('name'):
            name = call.data.split()[1]
            res = bd.show_trans(call.message, name)
            bot.send_message(call.message.chat.id, '+------------{}------------+'.format(name))
            if res != []:
                for row in res: 
                    row = list(row)
                    bot.send_message(call.message.chat.id, ' | '.join([str(el) for el in row if el != row[0]]))
                bot.send_message(call.message.chat.id, '{} сейчас должен {} руб.'.format(name, list(res)[-1][-1]))
            else:
                bot.send_message(call.message.chat.id, '{} не имеет задолжностей'.format(name))
            bot.send_message(call.message.chat.id, '+-----------------------------+')
    except Exception:
        bot.send_message(call.message.chat.id, "Вернитесь в меню и \nвведите запрос еще раз")


bot.polling(none_stop=True)