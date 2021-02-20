import sqlite3
import telebot
from telebot import types
import bd
from datetime import datetime
import time



# Функции контоллера

def menu(bot, message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Изменить размер долга", "Инфо", "Изменить км или страховку", "Добавить водителя", "Посадить водителя", "Добавить машину", "Удалить")
        send_mess = f"Что хотите сделать, {message.from_user.first_name}?"
        bot.send_message(message.chat.id, send_mess, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "Повторите запрос")
        menu(bot, message)


# def info(bot, message):
#     res = bd.pull_data()
#     menu(bot, message)

def info(bot, message):
    try:
        def review_drivers(message):
            res = bd.pull_data(message)
            if res != []:
                bot.send_message(message.chat.id, "<b>Водитель | ДР | Страховка | Долг | Машина | Км</b>", parse_mode='html')
                for row in res:
                    if row[-2] is None:
                        row = list(row)
                        row[-2] = 'Без машины'
                        row.remove(row[-1])
                    markup = types.InlineKeyboardMarkup()
                    btn = types.InlineKeyboardButton(text='{}. История платежей ->'.format(row[0]), callback_data='name '+row[0])
                    markup.add(btn)
                    bot.send_message(message.chat.id, ' | '.join([str(el) for el in row]), reply_markup=markup)
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, 'Еще нет ни одной записи')
                menu(bot, message)

        def review_cars(message):
            res = bd.pull_cars_info(message)
            if res != []:
                bot.send_message(message.chat.id, "<b>Номер | Машина | Км</b>", parse_mode='html')
                for i, row in enumerate(res):
                    row = list(row)
                    row.insert(0, i+1)
                    bot.send_message(message.chat.id, ' | '.join([str(el) for el in row]))
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, 'Еще нет ни одной записи')
                menu(bot, message)

        def select_info(message):
            if message.text == "Информация о водителях":
                review_drivers(message)
            elif message.text == "Информация о машинах":
                review_cars(message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Информация о водителях", "Информация о машинах")
        sent = bot.send_message(message.chat.id, "Выберете:", reply_markup=markup)
        bot.register_next_step_handler(sent, select_info)
    except Exception:
        bot.send_message(message.chat.id, "Ваш запрос непонятен,\nвведите запрос еще раз")

def car(bot, message):
    try:
        savedata = {}

        def accept7(message):
            if message.text == 'Да':
                bd.fill_row_car(message, savedata)
                res = bd.check_count(message)
                if int(res[0][0])%10 == 0:
                    bot.send_message(message.chat.id, 'У Вас уже {} машин!\nПоздравляю!'.format(res[0][0]))
                    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB5dZgMNXeu5lhqjEibHT05_igEKFUhAACsggAAgi3GQITL8y1531UoR4E')
                menu(bot, message)
            elif message.text == 'Повторить еще раз':
                car(bot, message)
            elif message.text == 'Перейти в меню': 
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def input_km(message):
            savedata["Пробег машины"] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Да", "Повторить еще раз", "Перейти в меню")
            sent = bot.send_message(message.chat.id, "Все введено верно?", reply_markup=markup)
            bot.register_next_step_handler(sent, accept7)

        def input_num(message):
            savedata["Госномер"] = message.text
            sent = bot.send_message(message.chat.id, "Введите пробег машины")
            bot.register_next_step_handler(sent, input_km)  

        sent = bot.send_message(message.chat.id, "Введите гос номер машины")
        bot.register_next_step_handler(sent, input_num)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)

def driver(bot, message):
    try:
        savedata = {}

        def accept(message):
            if message.text == 'Да':
                bd.fill_row_driver(message, savedata)
                menu(bot, message)
            elif message.text == 'Ввести заново':
                driver(bot, message)
            elif message.text == 'Перейти в меню': 
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def input_insurance_day(message):
            savedata["Дата последнего страхования"] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Да", "Ввести заново", "Перейти в меню")
            sent = bot.send_message(message.chat.id, "Все введено верно?", reply_markup=markup)
            bot.register_next_step_handler(sent, accept)

        def input_birthday(message):
            savedata["День рождения водителя"] = message.text
            sent = bot.send_message(message.chat.id, "Введите день последнего страхования водителя")
            bot.register_next_step_handler(sent, input_insurance_day)

        def input_name(message):
            savedata["Имя водителя"] = message.text
            sent = bot.send_message(message.chat.id, "Введите день рождения водителя")
            bot.register_next_step_handler(sent, input_birthday)

        sent = bot.send_message(message.chat.id, "Введите имя водителя")
        bot.register_next_step_handler(sent, input_name)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)

def delete_car(bot, message):
    try:
        data = {}

        def accept2(message):
            if message.text == 'Да':
                bd.delete_one_row(message, data['car'])
                menu(bot, message)
            elif message.text == 'Ввести заново':
                delete_car(bot, message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)
        
        def delete_row(message):
            data['car'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердите:', reply_markup=markup)
            bot.register_next_step_handler(sent, accept2)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.car_num(message)
        if res == []:
            bot.send_message(message.chat.id, "На данный момент информации по машинам нет")
            menu(bot, message)
        else:
            for i in res:
                markup.add(str(i[0]))
            sent = bot.send_message(message.chat.id, "Какую машину удалить?", reply_markup=markup)
            bot.register_next_step_handler(sent, delete_row)
    except Exception: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)

def delete_driver(bot, message):
    try:
        data = {}
        def accept3(message):
            if message.text == 'Да':
                bd.delete_driver(message, data['name'])
                menu(bot, message)
            elif message.text == 'Ввести заново':
                delete(bot, message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def del_driver2(message):
            data['name'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердите:', reply_markup=markup)
            bot.register_next_step_handler(sent, accept3)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.drivers_name(message)
        if res == []:
            bot.send_message(message.chat.id, "На данный момент информации по водителям нет")
            menu(bot, message)
        else:
            for i in res:
                markup.add(str(i[0]))
            sent = bot.send_message(message.chat.id, "Какого водителя убрать?", reply_markup=markup)
            bot.register_next_step_handler(sent, del_driver2)
    except Exception:
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)



def delete(bot, message):
    try:
        def select_del(message):
            if message.text == "Удалить машину":
                delete_car(bot, message)
            elif message.text == "Удалить водителя":
                delete_driver(bot, message)
            else:
                bot.send_message(message.chat.id, "Повторите запрос еще раз")
                menu(bot, message)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Удалить водителя", "Удалить машину")
        sent = bot.send_message(message.chat.id, "Выберете:", reply_markup=markup)
        bot.register_next_step_handler(sent, select_del)
    except Exception:
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)

def in_data(bot, message):
    try:
        data = {}
        def make_trans(message):
            if message.text == 'Да':
                bd.make_trans(message, data)
                menu(bot, message)
            elif message.text == 'Ввести заново':
                in_data(bot, message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)
    
        def acc(message):
            data['amount'] = float(message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, make_trans)
            
        def select_vec(message):
            if message.text == 'Погасить долг':
                data['sign'] = '-'
            elif message.text == 'Начислить долг':
                data['sign'] = '+'
            sent = bot.send_message(message.chat.id, 'Введите сумму:')
            bot.register_next_step_handler(sent, acc)
    
        def select_debt(message):
            data['name'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Погасить долг', 'Начислить долг')
            sent = bot.send_message(message.chat.id, 'Выберете:', reply_markup=markup)
            bot.register_next_step_handler(sent, select_vec)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.driver_names(message)
        for i in res:
            markup.add(str(i).strip("'(),'"))
        sent = bot.send_message(message.chat.id, 'Выберете имя водителя:', reply_markup=markup)
        bot.register_next_step_handler(sent, select_debt)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)

def in_km_ins(bot, message):
    try:
        data = {}

        def accept1(message):
            if message.text == 'Да':
                bd.make_new_km(message, data)
                menu(bot, message)
            elif message.text == 'Ввести заново':
                in_km_ins(bot, message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def km_agreed(message):
            data['km'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, accept1)

        def input_km(message):
            res = bd.car_km(message, message.text)
            data['number'] = message.text
            sent = bot.send_message(message.chat.id, 'Последнее обновление - <i><b>{}</b></i> км\nВведите новое состояние пробега:'.format(str(res).strip("[](),")), parse_mode='html')
            bot.register_next_step_handler(sent, km_agreed)

        def in_km(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            res = bd.car_num(message)
            for i in res:
                markup.add(str(i[0]))
            sent = bot.send_message(message.chat.id, 'Выберете машину', reply_markup=markup)
            bot.register_next_step_handler(sent, input_km)


        def accept8(message):
            if message.text == 'Да':
                bd.change_ins(message, data)
                menu(bot, message)
            elif message.text == 'Ввести заново':
                in_ins(message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def in_ins3(message):
            data['ins'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, accept8)


        def in_ins2(message):
            data['name'] = message.text
            res = bd.pull_date(message, data)
            sent = bot.send_message(message.chat.id, 'Последняя дата страхования - <i><b>{}</b></i>\nВведите дату нового страхования:'.format(str(res[0][0])), parse_mode='html')
            bot.register_next_step_handler(sent, in_ins3)

        def in_ins(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            res = bd.drivers_name(message)
            for i in res:
                markup.add(str(i[0]))
            sent = bot.send_message(message.chat.id, 'Выберете водителя:', reply_markup=markup)
            bot.register_next_step_handler(sent, in_ins2)

        def select_km_ins(message):
            if message.text == "Километраж":
                in_km(message)
            elif message.text == "Страховка":
                in_ins(message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)


        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Километраж", "Страховка")
        sent = bot.send_message(message.chat.id, 'Выберете, что изменить:', reply_markup=markup)
        bot.register_next_step_handler(sent, select_km_ins)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)
    
def driver_to_car(bot, message):
    try:
        data = {}

        def setting(message):
            if message.text == 'Да':
                bd.driver_to_car(message, data)
                menu(bot, message)
            elif message.text == 'Ввести заново':
                driver_to_car(bot, message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def accept6(message):
            if message.text == 'Без машины':
                data['gosnum'] = None
            else:
                data['gosnum'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, setting)


        def set_car(message):
            data['name'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            res = bd.car_num(message)
            for i in res:
                markup.add(str(i).strip("'(),'"))
            markup.add('Без машины')
            sent = bot.send_message(message.chat.id, 'Выберете машину', reply_markup=markup)
            bot.register_next_step_handler(sent, accept6)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.driver_names(message)
        for i in res:
            markup.add(str(i).strip("'(),'"))
        sent = bot.send_message(message.chat.id, 'Выберете имя водителя:', reply_markup=markup)
        bot.register_next_step_handler(sent, set_car)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)


def check_time(bot, message):
    while True:
        _td = datetime.today().strftime("%d.%m")
        _res = bd.check_ins(message)
        if _res != []:
            for el in _res:
                _i = el[0].split('.')
                _i[0] = int(_i[0]); _i[0]-=7; _i[1] = int(_i[1])
                if _i[0] <= 0:
                    _i[0] += 30; _i[1] -= 1
                    if _i[1] == 0:
                        _i[1] = 12
                if _i[1] < 10:
                    _i[1] = '0'+str(_i[1])
                else:  
                    _i[1] = str(_i[1])
                _st = str(_i[0])+'.'+_i[1]
                if _td == _st:
                    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB5dRgMNUbr3bgYTCnqu8_8T5laDcokQACFgADTlzSKY-vjYHMNYwJHgQ')
                    bot.send_message(message.chat.id, 'У водителя {} через неделю кончается страховка'.format(el[1]))
        time.sleep(86400) # ждет 1/2 день

# bot.send_chat_action(message.chat.id, 'typing') 