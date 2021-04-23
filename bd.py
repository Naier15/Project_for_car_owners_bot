import sqlite3
import pytz
from datetime import datetime

# Функции Базы данных

def create_db(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS cars (gosnum TEXT NOT NULL, km INTEGER, vari INTEGER);")  
        cursor.execute("CREATE TABLE IF NOT EXISTS drivers (name TEXT NOT NULL, birthday TEXT, insurance TEXT, debt REAL DEFAULT 0, gosnum TEXT, FOREIGN KEY (gosnum) REFERENCES car(gosnum));")
        cursor.execute("CREATE TABLE IF NOT EXISTS trans (name TEXT, date TEXT, refill TEXT, state_debt REAL);")
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:
        connection.close()

# def update(message):
#         try:
#             connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
#             cursor = connection.cursor()
#             cursor.execute("DROP TABLE IF EXISTS cars;")
#             cursor.execute("CREATE TABLE IF NOT EXISTS cars (gosnum TEXT NOT NULL, km INTEGER, vari INTEGER);")
#             connection.commit()
#         except sqlite3.Error:
#             print(sqlite3.Error)
#         finally:
#             connection.close()


def delete_one_row(message, row):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cars WHERE gosnum=?;", (row,))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def delete_driver(message, row):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM drivers WHERE name=?;", (row,))
        cursor.execute("DELETE FROM trans WHERE name=?;", (row,))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def fill_row_car(message, row):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cars (gosnum, km, vari) VALUES (?,?,?);", tuple(row.values()))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def fill_row_driver(message, row):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO drivers (name, birthday, insurance) VALUES (?,?,?);", tuple(row.values()))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()



def pull_data(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT name, birthday, insurance, debt, drivers.gosnum, km FROM drivers LEFT JOIN cars ON drivers.gosnum=cars.gosnum;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def car_num(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("SELECT gosnum FROM cars;")
        result = cursor.fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def pull_cars_info(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM cars;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def drivers_name(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT name FROM drivers;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def car_km(message, number):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("SELECT km FROM cars WHERE gosnum=?;", (number,))
        result = cursor.fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()



def driver_names(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT name FROM drivers;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def make_trans(message, data):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        time = datetime.now(pytz.timezone('Asia/Vladivostok')).strftime('%d.%m %H:%M')
        debt = cursor.execute("SELECT debt FROM drivers WHERE name=?;", (data['name'],)).fetchall()[0][0]

        if data['sign'] == '+':
            cursor.execute("INSERT INTO trans (name, date, refill, state_debt) VALUES (?, ?, ?, ?);", (data['name'], time, data['sign']+str(data['amount']), debt+data['amount']))
            cursor.execute("UPDATE drivers SET debt=? WHERE name=?;", (debt+data['amount'], data['name']))
        else: 
            cursor.execute("INSERT INTO trans (name, date, refill, state_debt) VALUES (?, ?, ?, ?);", (data['name'], time, data['sign']+str(data['amount']), debt-data['amount']))
            cursor.execute("UPDATE drivers SET debt=? WHERE name=?;", (debt-data['amount'], data['name']))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def make_new_km(message, data):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        if data['vari'] == 'Нет':
            cursor.execute("UPDATE cars SET km=? WHERE gosnum=?;", (data['km'], data['number']))
        elif data['vari'] == 'Да':
            cursor.execute("UPDATE cars SET km=?, vari=? WHERE gosnum=?;", (data['km'], data['km']+42000, data['number']))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def driver_to_car(message, data):

    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("UPDATE drivers SET gosnum=? WHERE name=?;", (data['gosnum'], data['name']))
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def show_trans(message, name):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM trans WHERE name=? LIMIT 10;", (name,)).fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def check_count(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT count(*) FROM cars;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close() 


def pull_date(message, data):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT insurance FROM drivers WHERE name=?;", (data['name'],)).fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close() 

def change_ins(message, data):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        cursor.execute("UPDATE drivers SET insurance=? WHERE name=?;", (data['ins'], data['name'])).fetchall()
        connection.commit()
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()

def check_ins(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT insurance, name FROM drivers;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()


def check_birth(message):
    try:
        connection = sqlite3.connect("{}.db".format(message.chat.id), check_same_thread = True)
        cursor = connection.cursor()
        result = cursor.execute("SELECT birthday, name FROM drivers;").fetchall()
        return result
    except sqlite3.Error:
        print(sqlite3.Error)
    finally:       
        connection.close()