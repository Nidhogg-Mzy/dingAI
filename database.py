import re
import json
from time import sleep
import mysql.connector


class DataBase:
    connection, cursor = None, None
    _database = None
    _config_file = "dbUserName.json"

    @staticmethod
    def set_config_file(filename: str) -> None:
        """
        This function sets the filename of database config file.
        :param filename A JSON file containing database connection configuration. Default value is 'dbUserName.json'
        """
        DataBase._config_file = filename

    @staticmethod
    def init_database() -> bool:
        """
        This method initialize the database connection, using the configuration in config file.
        If method 'set_config_file' is not invoked before, it uses 'dbUserName.json' as config file.
        :return True if connection is successfully established, False otherwise.
        """
        with open(DataBase._config_file, "r", encoding='utf-8') as f:
            temp = json.load(f)
            host, database, user, password = \
                temp["ip"], temp["database"], temp["username"], temp["password"]
            DataBase._database = database
        try:
            DataBase.connection = mysql.connector.connect(host=host,
                                                          database=database,
                                                          user=user,
                                                          password=password)
            DataBase.cursor = DataBase.connection.cursor()
            return True
        except mysql.connector.Error:
            return False

    @staticmethod
    def retry_if_disconnected(func):
        """
        A decorator to retry connecting to database, if the current connection is not working.
        This should be called before all function that requires db connection.
        """
        def wrapper(*args, **kwargs):
            # retry 5 times at most
            success = False
            for _ in range(5):
                # if the db is good, break the loop
                if (DataBase.connection is not None) and (DataBase.connection.is_connected()):
                    success = True
                    break
                # otherwise, try to init database
                if DataBase.init_database():
                    # if successfully connect, break the loop
                    success = True
                    break
                # otherwise, retry with a delay
                sleep(0.25)

            if not success:
                raise DatabaseDisconnectException("Failed to connect to database after 5 tries.")
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def close_database() -> None:   # TODO: when to call this method?
        DataBase.connection.close()
        DataBase.cursor.close()

    @staticmethod
    # TODO: refactor this method
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
    def insert_user(qq_account: str, username: str) -> None:
        """
        This method insert given user into database. We assume the parameters are valid.
        :param qq_account The qq account to insert
        :param username The leetcode username to insert
        """
        sql_cmd = f'INSERT INTO {DataBase._database}.Users (QQAccount, username) VALUES (%s, %s)'
        val = (qq_account, username)

        DataBase.cursor.execute(sql_cmd, val)
        DataBase.connection.commit()

    @staticmethod
    def get_user() -> dict:
        """
        This method retrieve all users from database, and return as a dictionary.
        :return A dict of all users, where key is qq_account, value is leetcode username.
        """
        sql_cmd = f'SELECT * FROM {DataBase._database}.Users'

        DataBase.cursor.execute(sql_cmd)
        users = DataBase.cursor.fetchall()

        return {user[0]: user[1] for user in users}

    @staticmethod
    def update_user(qq_account: str, username: str) -> None:
        """
        This method updates the leetcode account of the user with qq_account.
        :param qq_account The qq_account of the user to update
        :param username The new leetcode username of the user
        """
        sql_cmd = f'UPDATE {DataBase._database}.Users SET username = %s WHERE QQAccount = %s'
        val = (username, qq_account)

        DataBase.cursor.execute(sql_cmd, val)
        DataBase.connection.commit()

    @staticmethod
    def delete_user(qq_account: str) -> None:
        """
        This method deletes the user, given qq_account
        :param qq_account The qq_account of the user to be deleted.
        """
        sql_cmd = f'DELETE FROM {DataBase._database}.Users WHERE QQAccount = %s'

        DataBase.cursor.execute(sql_cmd, [qq_account])
        DataBase.connection.commit()


class DatabaseDisconnectException(Exception):
    """
    This exception will be raised if the database is failed to connect.
    """


if __name__ == '__main__':
    # d = DataBase()
    # d.insert_leetcode("2022-5-30", "test", "test", "test", "test", json.dumps(["Nidhogg-mzy", "enor2017"]))
    # print(d.get_user()[1])
    # d.update_user('34295782673', 'who loves zxy')
    # print(d.get_user()[1])
    # print("inserted successfully")

    DataBase.init_database()
    DataBase.get_user()
