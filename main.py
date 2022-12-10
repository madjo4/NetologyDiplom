import sqlite3

from vk_api.longpoll import VkEventType

from bot_model import write_msg, longpoll, write_hello_msg, send_search_response
from vk_client_model import VKClient

with open("user_token.txt", "r") as file_object:
    user_token = file_object.read().strip()


try:
    sqlite_connection = sqlite3.connect('vkinder.db')
    sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS recommendations (
                                user_vk_id INTEGER, 
                                partner_vk_id INTEGER, 
                                PRIMARY KEY(user_vk_id, partner_vk_id));'''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite создана")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if sqlite_connection:
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")


vk_client = VKClient(user_token)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request.lower() == "привет":
                write_hello_msg(vk_client, event.user_id)
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            if request.lower() == "искать":
                                send_search_response(vk_client, event.user_id)
                                for event in longpoll.listen():
                                    if event.type == VkEventType.MESSAGE_NEW:
                                        if event.to_me:
                                            request = event.text
                                            if request == "Хочу другой вариант":
                                                send_search_response(vk_client, event.user_id)
                                            elif request == "Спасибо. Достаточно":
                                                write_msg(event.user_id, "Отлично! Удачи. Для того, чтобы вернуться"
                                                                         " к поиску позже просто напишите 'привет'")
                                                break
                                            else:
                                                write_msg(event.user_id, "Извините. Я вас не понял. Для начала "
                                                                         "работы напишите, пожалуйста, 'привет' "
                                                                         "ещё раз.")
                                                break
                            elif request == 'Не нужно. Спасибо':
                                write_msg(event.user_id, "ОК. Если что, обращайся :)")
                                break
                            elif request.lower() == "привет":
                                write_msg(event.user_id, "Для начала работы напишите, пожалуйста, 'привет' ещё раз")
                                break
                            else:
                                write_msg(event.user_id, "Извините. Я вас не понял. Для начала работы напишите, "
                                                         "пожалуйста, 'привет' ещё раз.")
                                break
            else:
                write_msg(event.user_id, "Извините. Я вас не понял. Для начала общения со мной напишите 'привет'")
