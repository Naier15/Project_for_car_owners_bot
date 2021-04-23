from telebot import types
import bd
from datetime import datetime
import pytz
import time
import random
import schedule
import update


# Функции контоллера

def menu(bot, message):
    try:
        update.updating(bot, message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Долг", "Инфо", "Пробег или страховка", "Добавить водителя", "Посадить водителя", "Добавить машину", "Удалить", "Записки")
        send_mess = f"Что хотите сделать, {message.from_user.first_name}?"
        bot.send_message(message.chat.id, send_mess, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "Повторите запрос")
        menu(bot, message)


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
                    row = list(row)
                    row[0] = '<b>{}</b>'.format(row[0])
                    bot.send_message(message.chat.id, ' | '.join([str(el) for el in row]), parse_mode='html', reply_markup=markup)
                    bot.send_message(message.chat.id, '-----------------------------')
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, 'Еще нет ни одной записи')
                menu(bot, message)

        def review_cars(message):
            res = bd.pull_cars_info(message)
            if res != None and res != []:
                bot.send_message(message.chat.id, "<b>Номер | Машина | Км | Масло | Вариаторка</b>", parse_mode='html')
                for i, row in enumerate(res):
                    row = list(row)
                    row.insert(0, i+1)
                    row.insert(3, row[2]+7000)
                    bot.send_message(message.chat.id, ' | '.join([str(el) for el in row]))
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, 'Еще нет ни одной записи')
                menu(bot, message)

        def select_info(message):
            if message.text == "Водители":
                review_drivers(message)
            elif message.text == "Машины":
                review_cars(message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Водители", "Машины")
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
                if res != None and int(res[0][0])%10 == 0:
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

        def input_vari(message):
            try:
                savedata["vari"] = int(message.text)+42000
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add("Да", "Повторить еще раз", "Перейти в меню")
                sent = bot.send_message(message.chat.id, "Все введено верно?", reply_markup=markup)
                bot.register_next_step_handler(sent, accept7)
            except Exception:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def input_km(message):
            try:
                savedata["km"] = int(message.text)
                sent = bot.send_message(message.chat.id, "Введите пробег при последней замене вариаторки")
                bot.register_next_step_handler(sent, input_vari)
            except Exception:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message) 

        def input_num(message):
            savedata["gosnum"] = message.text
            sent = bot.send_message(message.chat.id, "Введите текущий пробег машины")
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
            try:
                data['amount'] = float(message.text)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add('Да', 'Ввести заново', 'Перейти в меню')
                sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
                bot.register_next_step_handler(sent, make_trans)
            except Exception as e:
                print(e)
                menu(bot, message)
            
        def select_vec(message):
            try:
                if message.text == 'Погасить долг' or message.text == 'Начислить долг':
                    if message.text == 'Погасить долг':
                        data['sign'] = '-'
                    elif message.text == 'Начислить долг':
                        data['sign'] = '+'
                    sent = bot.send_message(message.chat.id, 'Введите сумму:')
                    bot.register_next_step_handler(sent, acc)
                else:
                    bot.send_message(message.chat.id, "Повторите запрос еще раз")
                    menu(bot, message)
            except Exception as e:
                print(e)
                menu(bot, message)
    
        def select_debt(message):
            try:
                data['name'] = message.text
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add('Погасить долг', 'Начислить долг')
                sent = bot.send_message(message.chat.id, 'Выберете:', reply_markup=markup)
                bot.register_next_step_handler(sent, select_vec)
            except Exception as e:
                print(e)
                menu(bot, message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.driver_names(message)
        for i in res:
            markup.add(i[0])
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
            data['vari'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, accept1)

        def sel_vari(message):
            try:
                data['km'] = int(message.text)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add('Да', 'Нет')
                sent = bot.send_message(message.chat.id, 'Поменяли вариаторку?', reply_markup=markup)
                bot.register_next_step_handler(sent, km_agreed)
            except Exception as e: 
                bot.send_message(message.chat.id, "Повторите запрос еще раз")
                menu(bot, message)

        def input_km(message):
            res = bd.car_km(message, message.text)
            data['number'] = message.text
            sent = bot.send_message(message.chat.id, 'Последнее обновление - <i><b>{}</b></i> км\nВведите новое состояние пробега:'.format(str(res[0][0])), parse_mode='html')
            bot.register_next_step_handler(sent, sel_vari)

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
            if message.text == "Пробег":
                in_km(message)
            elif message.text == "Страховка":
                in_ins(message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)


        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Пробег", "Страховка")
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
                markup.add(i[0])
            markup.add('Без машины')
            sent = bot.send_message(message.chat.id, 'Выберете машину', reply_markup=markup)
            bot.register_next_step_handler(sent, accept6)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        res = bd.driver_names(message)
        for i in res:
            markup.add(i[0])
        sent = bot.send_message(message.chat.id, 'Выберете имя водителя:', reply_markup=markup)
        bot.register_next_step_handler(sent, set_car)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)


def notes(bot, message):
    
    try:
        data = {}

        def del_note1(message):
            try:
                with open('notes.txt', 'rt') as file:
                    data = file.read()
                    data1 = data.replace(res[int(message.text.split(maxsplit=1)[0])-1]+'\n', '')
                    with open('notes.txt', 'w') as file:
                        file.write(data1)
                menu(bot, message)
            except Exception as e: 
                bot.send_message(message.chat.id, "Повторите запрос еще раз")
                menu(bot, message)

        def del_note(message):
            try:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                global res
                with open('notes.txt', 'rt') as file:
                    res = file.read().split('\n')
                res = list(filter(None, res))
                for i, el in enumerate(res): 
                    markup.add(str(i+1)+' '+el[:len(el)-1]) if len(el) < 25 else markup.add(str(i+1)+' '+el[:24])  
                sent = bot.send_message(message.chat.id, 'Какую записку удалить?', reply_markup=markup)
                bot.register_next_step_handler(sent, del_note1)
            except Exception as e: 
                bot.send_message(message.chat.id, "Повторите запрос еще раз")
                menu(bot, message)

        def show_note(message):
            try:
                bot.send_message(message.chat.id, res[int(message.text.split()[0])-1])
                menu(bot, message)
            except Exception as e: 
                bot.send_message(message.chat.id, "Повторите запрос еще раз")
                menu(bot, message)
            
        def all_notes(message):
            try:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                global res
                with open('notes.txt') as file:
                    res = file.read().split('|\n')
                res = list(filter(None, res))
                if res != []:
                    for i, el in enumerate(res): 
                        markup.add(str(i+1)+' | '+el[:len(el)-1]) if len(el) < 25 else markup.add(str(i+1)+' | '+el[:24])           
                    sent = bot.send_message(message.chat.id, 'Выберете записку:', reply_markup=markup)
                    bot.register_next_step_handler(sent, show_note)
                else:
                    bot.send_message(message.chat.id, 'Сейчас нет никаких записей')
                    menu(bot, message)
            except Exception:
                bot.send_message(message.chat.id, 'Сейчас записей нет')
                menu(bot, message)

        def accept9(message):
            if message.text == 'Да':
                with open('notes.txt', 'a') as file:
                    file.write(data['text'] + '\t|\n')
                menu(bot, message)
            elif message.text == 'Ввести заново':
                make_note(message)
            elif message.text == 'Перейти в меню':
                menu(bot, message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        def make_note1(message):
            data['text'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Ввести заново', 'Перейти в меню')
            sent = bot.send_message(message.chat.id, 'Подтвердить?', reply_markup=markup)
            bot.register_next_step_handler(sent, accept9)

        def make_note(message):
            sent = bot.send_message(message.chat.id, 'Излагайте...')
            bot.register_next_step_handler(sent, make_note1)

        def act_notes(message):
            if message.text == "Просмотреть записи":
                all_notes(message)
            elif message.text == "Написать новую":
                make_note(message)
            elif message.text == "Удалить запись":
                del_note(message)
            else:
                bot.send_message(message.chat.id, "Вернитесь в меню и \nповторите запрос")
                menu(bot, message)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Просмотреть записи", "Написать новую", "Удалить запись")
        sent = bot.send_message(message.chat.id, 'Выберете:', reply_markup=markup)
        bot.register_next_step_handler(sent, act_notes)
    except Exception as e: 
        bot.send_message(message.chat.id, "Повторите запрос еще раз")
        menu(bot, message)



greet =('CAACAgIAAxkBAAEB5-RgMp_gPkn2IWooA6oJnFqOCjYoVAAC0QAD9wLID7DVFiL6IbHMHgQ',
        'CAACAgIAAxkBAAEB5-BgMp--OztBOsh9brdaNAUebcyj9QACSwcAAkb7rASYwmXoo2kPLh4E',
        'CAACAgIAAxkBAAEB58NgModFO3FHUYC7Nlris0MFVaWSXwACpwIAAkcGQwUdTGgQM2X2OR4E',
        'CAACAgIAAxkBAAEB5-ZgMqC8iCVI0-Rv7WnaA9ob4LvJ7AACWQADrWW8FPS7RxeJ4S0JHgQ',
        'CAACAgIAAxkBAAEB5-hgMqDFGhz8REk3jwABbf-y0RnXME0AAhoAAztgJBSGOmsn7rOOZR4E',
        'CAACAgIAAxkBAAEB5-pgMqDM4YHeKjLdiBlp8_umnrs8DwACJwADr8ZRGpVmnh4Ye-0RHgQ',
        'CAACAgIAAxkBAAEB5-xgMqPMIWVbRUszoOBHXZDFwIzvuwACOgADr8ZRGutCYzxwMcBJHgQ',
        'CAACAgIAAxkBAAEB5-5gMqPzm5OUBmRNnyeD6kZKMKXvxAACFAADr8ZRGgu7XTT4sVnxHgQ')

def check_time(bot, message):
        _td = datetime.now(pytz.timezone('Asia/Vladivostok')).strftime("%d.%m")
        _res = bd.check_ins(message)
        _birth = bd.check_birth(message)
        if _birth != None and _birth != []:
            for el in _birth:
                if el[0] == _td:
                        bot.send_sticker(message.chat.id, random.choice(greet))
                        bot.send_message(message.chat.id, '{} сегодня празднует свой день рождения!\nНе забудьте его поздравить!'.format(el[1]))
        
        if _td == '13.06':
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB6d9gNS7-idkHxfwKFlaTVaO7NnGOIQACLAEAArnzlwtfk8YcW4wyZh4E')
            bot.send_message(message.chat.id, 'Виталий,\nОт всего процессора поздравляю Вас с днем рождения!\nЖелаю в этот день, как впрочем и всегда, чтобы Вы чувствовали себя лучше всех! Не ржавели механизмы!\nА рядом были только нужные и любимые люди!')
        
        if _td == '23.02':
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB6dNgNSiGcYntxRFe2JQOg4OASpRhlQACNwEAAuSgzgcq2qkVHprsbR4E')
            bot.send_message(message.chat.id, 'С настоящим мужским праздником!')
        
        if _td == '31.12':
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB6dlgNSzq0Y8HpYT_LfOihMkCcMCGAwACNQAD5lSWFWcmVf9XZ3gnHgQ')
            bot.send_message(message.chat.id, 'Вижу год был продуктивным...\nНо новый обязательно будет еще лучше!\nС Новым годом!')
        
        if _res != None and _res != []:
            for el in _res:
                _i = list(map(int, el[0].split('.')))
                _i[0]-=21
                if _i[0] <= 0:
                    _i[0] += 30; _i[1] -= 1
                    if _i[1] == 0:
                        _i[1] = 12
                _i[1] = '0' + str(_i[1]) if _i[1] < 10 else str(_i[1])
                if _td == (str(_i[0])+'.'+_i[1]):
                            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB5dRgMNUbr3bgYTCnqu8_8T5laDcokQACFgADTlzSKY-vjYHMNYwJHgQ')
                            bot.send_message(message.chat.id, 'У водителя {} через 3 недели кончается страховка'.format(el[1]))

sunday_alarm = ('CAACAgIAAxkBAAEB6d1gNS6pMvOIWr8LduRpsVzyS__0DQACZwEAArnzlwtb5cjTEhFi6x4E',
                'CAACAgIAAxkBAAEB6wdgNrJlyFvGGW0GGPHRfivCB6KW9wAC5QMAAkcVaAltmiQllMWuHx4E',
                'CAACAgIAAxkBAAEB6wlgNrJ1QWPLgqeLieShhE4zk6sU3wACAwEAAladvQoC5dF4h-X6Tx4E',
                'CAACAgIAAxkBAAEB6wtgNrKR7JT4Q-PAfeKLFPh1Hj6U_wACBAEAAvcCyA8gD3c76avISR4E',
                'CAACAgIAAxkBAAEB6w1gNrKXcSoIQ4F9NYULV2vy9w_4TQACTwEAAiI3jgR8lZdITHG8Fx4E',
                'CAACAgIAAxkBAAEB6w9gNrNcc4ddmIiWRjCB292ql88cugACVQYAAvoLtgjB7ZVI0sveYR4E',
                'CAACAgIAAxkBAAEB6xFgNrNmmn6Ltwc1CzBRLR_0E7G34wACHwADTlzSKeq-C6KWSlvuHgQ',
                'CAACAgIAAxkBAAEB6xNgNrNvpLwJwKAH1dhluMVX49XqwQAC4wADECECECB2Kq2OTKzyHgQ')

def alarm(bot, message):
    bot.send_sticker(message.chat.id, random.choice(sunday_alarm))
    bot.send_message(message.chat.id, 'У-у-у...\nКажется сегодня воскресение!\nМожно немного постричь капусту')

def run(bot, message):
    schedule.every().day.at("01:00").do(check_time, bot = bot, message = message)
    schedule.every().sunday.at("01:00").do(alarm, bot = bot, message = message)

    while cycle: 
        schedule.run_pending() 
        time.sleep(1)

# bot.send_chat_action(message.chat.id, 'typing') 