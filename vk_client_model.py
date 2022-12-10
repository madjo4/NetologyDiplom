import requests

from db_model import check_recommendation


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
        if response.json()['response']:
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
                print("В вашем профиле отсутствует информация как минимум по одному из параметров: "
                      "возраст, пол, город или семейное положение. Для работы с программой, пожалуйста, "
                      "обновите ваш профиль и возвращайтесь.")
        else:
            print('Ошибка получения данных от сервера')

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
        response = requests.get(url, params={**params})
        if response.json()['response']['items']:
            partner_list = []
            for item in response.json()['response']['items']:
                if item['is_closed'] is True:
                    continue
                else:
                    partner_list.append(item['id'])
            verified_partner_list = []
            for element in partner_list:
                db_check = check_recommendation(search_params[6], element)
                if db_check == 'Повтор':
                    continue
                else:
                    verified_partner_list.append(element)
            if verified_partner_list:
                return verified_partner_list
            else:
                return None
        else:
            print('Ошибка получения данных от сервера')

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
        if response.json()['response']['items']:
            photo_dict = {}
            for item in response.json()['response']['items']:
                for photo in item:
                    photo_dict[item['id']] = item['comments']['count'] + item['likes']['count']
            sorted_photos = dict(sorted(photo_dict.items(), key=lambda item: item[1], reverse=True))
            return list(sorted_photos.keys())[:3]
        else:
            print('Ошибка получения данных от сервера')
