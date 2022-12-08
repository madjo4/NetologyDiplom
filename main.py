import sqlite3

import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import requests


with open("user_token.txt", "r") as file_object:
    user_token = file_object.read().strip()

with open("group_token.txt", "r") as file_object:
    group_token = file_object.read().strip()

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
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")


def insert_recommendation_into_table(user_id, partner_id):
    try:
        sqlite_connection = sqlite3.connect('vkinder.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO recommendations
                              (user_vk_id, partner_vk_id)
                              VALUES (?, ?);"""

        data_tuple = (user_id, partner_id)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу vkinder.db")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def check_recommendation(user_id, partner_id):
    try:
        sqlite_connection = sqlite3.connect('vkinder.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from recommendations where user_vk_id = ? and partner_vk_id = ?"""
        cursor.execute(sql_select_query, (user_id,partner_id))
        records = cursor.fetchall()
        if records:
            return 'Повтор'
        else:
            return 'ОК'

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


class VKClient:
    def __init__(self, user_token, api_version='5.131'):
        self.token = user_token
        self.api_version = api_version

    def get_user_info(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': self.token,
            'user_id': user_id,
            'v': self.api_version,
            'fields': 'bdate, sex, city, relation',
        }
        response = requests.get(url, params={**params})
        user_key_info = []
        for item in response.json()['response']:
            try:
                user_key_info.append(item['first_name'])
            except KeyError:
                print("Не указано имя")
            try:
                user_key_info.append(item['last_name'])
            except KeyError:
                print("Не указана фамилия")
            try:
                user_key_info.append(item['bdate'].split(".")[2])
            except IndexError:
                print("Не указан год рождения")
            except KeyError:
                print("Нет даты рождения")
            try:
                user_key_info.append(item['sex'])
            except KeyError:
                print("Не указан пол")
            try:
                user_key_info.append(item['city']['id'])
            except KeyError:
                print("Не указан город")
            try:
                user_key_info.append(item['relation'])
            except KeyError:
                print("Не указано семейное положение")
            user_key_info.append(item['id'])
        if len(user_key_info) == 7:
            return user_key_info
        else:
            print("В вашем профиле отсутствует информация как минимум по одному из параметров: возраст, пол, город или"
                  " семейное положение. Для работы с программой, пожалуйста, обновите ваш профиль и возвращайтесь.")


    def search_partners(self, search_params: list, sorting=0, count=1000):
        url = 'https://api.vk.com/method/users.search'
        global search_sex
        if search_params[3] == 1:
            search_sex = 2
        elif search_params[3] == 2:
            search_sex = 1
        else:
            print('У вас в профиле не указан пол. Подбор не возможен.')
        params = {
            'access_token': self.token,
            'sort': sorting,
            # 'offset': randrange(100),
            'count': count,
            'v': self.api_version,
            'fields': 'bdate, sex, city, relation',
            'status': '6',
            'birth_year': search_params[2],
            'sex': search_sex,
            'city_id': search_params[4],
        }
        # blank_response = {'response': {'count': 39014, 'items': []}}
        response = requests.get(url, params={**params})
        # return response.json()
        partner_list = []
        for item in response.json()['response']['items']:
            if item['is_closed'] == True:
                continue
            else:
                partner_list.append(item['id'])
        return partner_list

    def choose_partner(self, partner_list: list):
        return random.choice(partner_list)

    def get_top3_photo(self, owner_id: int):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token,
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': 1,
            'v': self.api_version
        }
        response = requests.get(url, params={**params})
        photo_dict = {}
        for item in response.json()['response']['items']:
            for photo in item:
                photo_dict[item['id']] = item['comments']['count'] + item['likes']['count']
        sorted_photos = dict(sorted(photo_dict.items(), key=lambda item: item[1], reverse=True))
        return list(sorted_photos.keys())[:3]


def write_msg(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7)})


def write_question_msg(user_id, message, keyboard):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard,  'random_id': random.randrange(10 ** 7)})


def send_partner_photos(user_id, partner_id, photo_ids: list):
    for photo in photo_ids:
        vk_bot.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(10 ** 7),
        'attachment': f"photo{partner_id}_{photo}"})


vk_bot = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_bot)

vk_client = VKClient(user_token)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request.lower() == "привет":
                user_info = vk_client.get_user_info(event.user_id)
                if user_info == None:
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
                                    partner_recommendation = vk_client.choose_partner(partner_options)
                                    db_check = check_recommendation(event.user_id, partner_recommendation)
                                    while db_check == 'Повтор':
                                        partner_recommendation = vk_client.choose_partner(partner_options)
                                        db_check = check_recommendation(event.user_id, partner_recommendation)
                                    insert_recommendation_into_table(event.user_id, partner_recommendation)
                                    partner_photos = vk_client.get_top3_photo(partner_recommendation)
                                    write_msg(event.user_id, f"Хочешь познакомиться с https://vk.com/id{partner_recommendation} ?")
                                    send_partner_photos(event.user_id, partner_id=partner_recommendation, photo_ids=partner_photos)
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
                                                    partner_recommendation = vk_client.choose_partner(partner_options)
                                                    db_check = check_recommendation(event.user_id,
                                                                                    partner_recommendation)
                                                    while db_check == 'Повтор':
                                                        partner_recommendation = vk_client.choose_partner(
                                                            partner_options)
                                                        db_check = check_recommendation(event.user_id,
                                                                                        partner_recommendation)
                                                    insert_recommendation_into_table(event.user_id,
                                                                                     partner_recommendation)
                                                    partner_photos = vk_client.get_top3_photo(partner_recommendation)
                                                    write_msg(event.user_id,
                                                              f"Хочешь познакомиться с https://vk.com/id{partner_recommendation} ?")
                                                    send_partner_photos(event.user_id, partner_id=partner_recommendation,
                                                                        photo_ids=partner_photos)
                                                    write_question_msg(event.user_id, f"Достаточно или ищем ещё?",
                                                                       keyboard=keyboard2.get_keyboard())
                                                elif request == "Спасибо. Достаточно":
                                                    write_msg(event.user_id, "Отлично! Удачи. Для того, чтобы вернуться к поиску позже просто напишите 'привет'.")
                                                    break
                                                else:
                                                    write_msg(event.user_id, "Извините. Не вас понял. Для начала работы напишите, пожалуйста, 'привет' ещё раз.")
                                                    break
                                elif request == 'Не нужно. Спасибо':
                                    write_msg(event.user_id, "ОК. Если что, обращайся :)")
                                    break
                                elif request.lower() == "привет":
                                    write_msg(event.user_id, "Для начала работы напишите, пожалуйста, 'привет' ещё раз.")
                                    break
                                else:
                                    write_msg(event.user_id, "Извините. Не вас понял. Для начала работы напишите, пожалуйста, 'привет' ещё раз.")
                                    break
            else:
                write_msg(event.user_id, "Извините. Я вас не понял. Для начала общения со мной напишите 'привет'")
#
# user1 = vk_client.get_user_info(5485627)
# print(user1)
# options = vk_client.search_partners(user1)
# print(options)

# insert_recommendation_into_table(20184634, 5485627)
# insert_recommendation_into_table(20184634, 814620)
# insert_recommendation_into_table(20184634, 1456321)
# # read_sqlite_table()
# # get_user_info(20184634)
# check_recommendation(20184634, 1456320)
