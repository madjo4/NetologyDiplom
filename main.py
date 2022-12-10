import sqlite3

import random

from vk_api.longpoll import VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from bot_model import write_msg, write_question_msg, send_partner_photos, longpoll
from db_model import check_recommendation, insert_recommendation_into_table
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
                user_info = vk_client.get_user_info(event.user_id)
                if user_info is None:
                    write_msg(event.user_id, f"Привет, пользователь! В вашем профиле отсутствует информация как "
                                             f"минимум по одному из параметров: возраст, пол, город или семейное "
                                             f"положение. Для работы с программой, пожалуйста, обновите ваш профиль "
                                             f"и возвращайтесь.")
                else:
                    write_msg(event.user_id, f"Привет, {user_info[0]}!")
                    keyboard = VkKeyboard(inline=True)
                    keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('Не нужно. Спасибо', color=VkKeyboardColor.PRIMARY)
                    write_question_msg(event.user_id, f"Найдём тебе пару?", keyboard=keyboard.get_keyboard())
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request.lower() == "искать":
                                    partner_options = vk_client.search_partners(user_info)
                                    partner_recommendation = random.choice(partner_options)
                                    db_check = check_recommendation(event.user_id, partner_recommendation)
                                    while db_check == 'Повтор':
                                        partner_recommendation = random.choice(partner_options)
                                        db_check = check_recommendation(event.user_id, partner_recommendation)
                                    insert_recommendation_into_table(event.user_id, partner_recommendation)
                                    partner_photos = vk_client.get_top3_photo(partner_recommendation)
                                    write_msg(event.user_id, f"Хочешь познакомиться с "
                                                             f"https://vk.com/id{partner_recommendation} ?")
                                    send_partner_photos(event.user_id, partner_id=partner_recommendation,
                                                        photo_ids=partner_photos)
                                    keyboard2 = VkKeyboard(inline=True)
                                    keyboard2.add_button('Хочу другой вариант', color=VkKeyboardColor.PRIMARY)
                                    keyboard2.add_button('Спасибо. Достаточно', color=VkKeyboardColor.PRIMARY)
                                    write_question_msg(event.user_id, f"Достаточно или ищем ещё?",
                                                       keyboard=keyboard2.get_keyboard())
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW:
                                            if event.to_me:
                                                request = event.text
                                                if request == "Хочу другой вариант":
                                                    partner_options = vk_client.search_partners(user_info)
                                                    partner_recommendation = random.choice(partner_options)
                                                    db_check = check_recommendation(event.user_id,
                                                                                    partner_recommendation)
                                                    while db_check == 'Повтор':
                                                        partner_recommendation = random.choice(partner_options)
                                                        db_check = check_recommendation(event.user_id,
                                                                                        partner_recommendation)
                                                    insert_recommendation_into_table(event.user_id,
                                                                                     partner_recommendation)
                                                    partner_photos = vk_client.get_top3_photo(partner_recommendation)
                                                    write_msg(event.user_id,
                                                              f"Хочешь познакомиться с "
                                                              f"https://vk.com/id{partner_recommendation} ?")
                                                    send_partner_photos(event.user_id,
                                                                        partner_id=partner_recommendation,
                                                                        photo_ids=partner_photos)
                                                    write_question_msg(event.user_id, f"Достаточно или ищем ещё?",
                                                                       keyboard=keyboard2.get_keyboard())
                                                elif request == "Спасибо. Достаточно":
                                                    write_msg(event.user_id, "Отлично! Удачи. Для того, чтобы вернуться"
                                                                             " к поиску позже просто напишите 'привет'")
                                                    break
                                                else:
                                                    write_msg(event.user_id, "Извините. Не вас понял. Для начала "
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
                                    write_msg(event.user_id, "Извините. Не вас понял. Для начала работы напишите, "
                                                             "пожалуйста, 'привет' ещё раз.")
                                    break
            else:
                write_msg(event.user_id, "Извините. Я вас не понял. Для начала общения со мной напишите 'привет'")
