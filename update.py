import control
import threading

def updating(bot, message):
    global thread
    if 'thread' in globals():
        control.cycle = False
        thread.join()
    control.cycle = True
    thread = threading.Thread(target=control.run, args=(bot, message)) 
    thread.start()

def close():
    try:
        global thread
        control.cycle = False
        thread.join()
        print('Уведомления отключены')
    except Exception:
        print('Отключить не удалось')