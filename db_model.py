import sqlite3


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
        cursor.execute(sql_select_query, (user_id, partner_id))
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
