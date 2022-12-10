import random

import vk_api
from vk_api.longpoll import VkLongPoll

with open("group_token.txt", "r") as file_object:
    group_token = file_object.read().strip()

vk_bot = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_bot)

def write_msg(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7)})


def write_question_msg(user_id, message, keyboard):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard,
                                    'random_id': random.randrange(10 ** 7)})


def send_partner_photos(user_id, partner_id, photo_ids: list):
    for photo in photo_ids:
        vk_bot.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(10 ** 7),
                                        'attachment': f"photo{partner_id}_{photo}"})
