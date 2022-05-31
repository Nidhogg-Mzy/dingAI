import mysql.connector
from mysql.connector import Error
import json
import re


class DataBase:
    with open("dbUserName.json", "r", encoding='utf-8') as f:
        temp = json.load(f)
        host, database, user, password = \
            temp["ip"], temp["database"], temp["username"], temp["password"]

    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=user,
                                             password=password)
        cursor = connection.cursor()
    except Error as e:
        print("Error while connecting to MySQL", e)

    @staticmethod
    def insert_leetcode(date: str, id_: str, link: str, difficult: str, description: str, participants: json):
        if date is None:
            mySql = 'INSERT INTO test.LeetCode (id, link, difficulty, description, participants) ' \
                    'VALUES (%s, %s, %s, %s, %s)'
            val = (id_, link, difficult, description, participants)
            DataBase.cursor.execute(mySql, val)
            DataBase.connection.commit()
        elif re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", date):
            # need to add a re to check if date is in the correct format
            mySql = 'INSERT INTO test.LeetCode (date, id, link, difficulty, description, participants) ' \
                    'VALUES (%s, %s, %s, %s, %s, %s)'
            val = (date, id_, link, difficult, description, participants)
            DataBase.cursor.execute(mySql, val)
            DataBase.connection.commit()
        else:
            print("Input error, please check input format")

    @staticmethod
    def insert_user(QQAccount: str, username: str) -> bool:
        mySql = 'INSERT INTO test.Users (QQAccount, username) VALUES (%s, %s)'
        val = (QQAccount, username)
        for i in range(2):
            if not DataBase.connection.is_connected():
                DataBase.connect_to_database()
        try:
            DataBase.cursor.execute(mySql, val)
            DataBase.connection.commit()
            return True
        except Error:
            return False
        finally:
            if DataBase.connection.is_connected():
                DataBase.cursor.close()
                DataBase.connection.close()
                print("MySQL connection is closed")

    @staticmethod
    def get_user() -> tuple:
        mySql = 'SELECT * FROM test.Users'
        for i in range(2):
            if not DataBase.connection.is_connected():
                DataBase.connect_to_database()
        toReturn = {}
        try:
            DataBase.cursor.execute(mySql)
            users = DataBase.cursor.fetchall()
            for user in users:
                toReturn[user[0]] = user[1]
            return True, toReturn
        except Error:
            return False, toReturn

    @staticmethod
    def update_user(QQAccount: str, username: str) -> bool:
        mySql = 'UPDATE test.Users SET username = %s WHERE QQAccount = %s'
        val = (username, QQAccount)
        try:
            DataBase.cursor.execute(mySql, val)
            DataBase.connection.commit()
            return True
        except Error:
            return False

    @staticmethod
    def delete_user(QQAccount: str) -> bool:
        mySql = 'DELETE FROM test.Users WHERE QQAccount = %s'
        for i in range(2):
            if not DataBase.connection.is_connected():
                DataBase.connect_to_database()
        try:
            DataBase.cursor.execute(mySql, QQAccount)
            DataBase.connection.commit()
            return True
        except Error:
            return False

    @staticmethod
    def connect_to_database():
        DataBase.connection = mysql.connector.connect(host=DataBase.host,
                                                      database=DataBase.database,
                                                      user=DataBase.user,
                                                      password=DataBase.password)


if __name__ == '__main__':
    d = DataBase()
    # d.insert_leetcode("2022-5-30", "test", "test", "test", "test", json.dumps(["Nidhogg-mzy", "enor2017"]))
    d.get_user()
    d.update_user('34295782673', 'sb')
    d.get_user()
    # print("inserted successfully")
