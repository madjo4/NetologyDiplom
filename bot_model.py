import random

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll

from db_model import insert_recommendation_into_table

with open("group_token.txt", "r") as file_object:
    group_token = file_object.read().strip()

vk_bot = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_bot)


def write_msg(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7)})


def write_question_msg(user_id, message, keyboard):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard,
                                    'random_id': random.randrange(10 ** 7)})


def write_hello_msg(vk_client, user_id):
    user_info = vk_client.get_user_info(user_id)
    if user_info is None:
        write_msg(user_id, f"Привет, пользователь! В вашем профиле отсутствует информация как минимум по одному из "
                           f"параметров: возраст, пол, город или семейное положение. Для работы с программой, "
                           f"пожалуйста, обновите ваш профиль и возвращайтесь.")
    else:
        write_msg(user_id, f"Привет, {user_info[0]}!")
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Не нужно. Спасибо', color=VkKeyboardColor.PRIMARY)
        write_question_msg(user_id, f"Найдём тебе пару?", keyboard=keyboard.get_keyboard())


def send_partner_photos(user_id, partner_id, photo_ids: list):
    if photo_ids:
        for photo in photo_ids:
            vk_bot.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(10 ** 7),
                                            'attachment': f"photo{partner_id}_{photo}"})
    else:
        print('Нет доступных фото в профиле')


def send_search_response(vk_client, user_id):
    user_info = vk_client.get_user_info(user_id)
    partner_options = vk_client.search_partners(user_info)
    partner_recommendation = random.choice(partner_options)
    insert_recommendation_into_table(user_id, partner_recommendation)
    partner_photos = vk_client.get_top3_photo(partner_recommendation)
    write_msg(user_id, f"Хочешь познакомиться с https://vk.com/id{partner_recommendation} ?")
    send_partner_photos(user_id, partner_id=partner_recommendation, photo_ids=partner_photos)
    keyboard2 = VkKeyboard(inline=True)
    keyboard2.add_button('Хочу другой вариант', color=VkKeyboardColor.PRIMARY)
    keyboard2.add_button('Спасибо. Достаточно', color=VkKeyboardColor.PRIMARY)
    write_question_msg(user_id, f"Достаточно или ищем ещё?", keyboard=keyboard2.get_keyboard())
