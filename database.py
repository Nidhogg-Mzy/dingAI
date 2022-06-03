import datetime
import json
from time import sleep
import mysql.connector


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
    def close_database() -> None:  # TODO: when to call this method?
        DataBase.connection.close()
        DataBase.cursor.close()

    @staticmethod
    @retry_if_disconnected
    def insert_leetcode(id_: str, name: str, link: str, difficult: str, description: str):
        """
        This method insert leetcode question into table leetcode in database
        """
        sql_cmd = 'INSERT INTO test.LeetCode (id, name, link, difficulty, description) ' \
                  'VALUES (%s, %s, %s, %s, %s)'
        val = (id_, name, link, difficult, description)
        DataBase.cursor.execute(sql_cmd, val)
        DataBase.connection.commit()

    @staticmethod
    @retry_if_disconnected
    def insert_studyOn(id_: str, date=None) -> None:
        """
        This method insert a new record to the table StudyOn,
        should give user message after return False(implement in LeetCode.py)
        """
        sql_cmd = 'INSERT INTO test.StudyOn(date, id) VALUES (%s, %s)'
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            val = (date, id_)
        else:
            val = (date, id_)
        DataBase.cursor.execute(sql_cmd, val)
        DataBase.connection.commit()

    @staticmethod
    @retry_if_disconnected
    def get_question_on_date(date: str) -> dict:
        """
        This method get all the question on a specific date

        """
        sql_cmd = 'SELECT id FROM test.StudyOn WHERE date = %s'
        val = date
        DataBase.cursor.execute(sql_cmd, val)
        questions = DataBase.cursor.fetchall()
        return {date: questions}

    @staticmethod
    @retry_if_disconnected
    def check_user_finish_problem(date: str, problem_id: str, qq: str) -> bool:
        """
        This function only checks if the user (identified by qq) has finished the given problem
        on given date in database record. This will not invoke Leetcode API to do online checking.

        :param date The date of given problem
        :param problem_id The unique id of problem, not problem name
        :param qq The qq account of user
        :return True if database has the record that user finished given problem on given date
        """
        sql_cmd = 'SELECT participant FROM test.ParticipateIn WHERE date = %s AND id = %s'
        val = (date, problem_id)
        DataBase.cursor.execute(sql_cmd, val)
        participants = DataBase.cursor.fetchall()
        if qq in participants:
            return True
        return False

    @staticmethod
    @retry_if_disconnected
    def submit_problem(date: str, problem_id: str, qq: str) -> None:
        """
        This function will be called when a user successfully submits the problem.

        :param date The date of given problem
        :param problem_id The unique id of problem, not problem name
        :param qq The qq account of user
        """
        sql_cmd = 'INSERT INTO test.ParticipateIn (date, id, participant) VALUES (%s, %s, %s)'
        val = (date, problem_id, qq)
        DataBase.cursor.execute(sql_cmd, val)
        DataBase.connection.commit()

    @staticmethod
    @retry_if_disconnected
    def get_prob_participant(date: str, problem_id: str) -> list:
        """
        This function get all participants for given problem on given date.

        :param date The date of given problem
        :param problem_id The unique id of problem, not problem name
        :return A list containing all users (identified by qq) that have submitted the problem
        """
        sql_cmd = 'SELECT participant FROM test.ParticipateIn WHERE date = %s AND id = %s'
        val = (date, problem_id)
        DataBase.cursor.execute(sql_cmd, val)
        return DataBase.cursor.fetchall()

    @staticmethod
    @retry_if_disconnected
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
    @retry_if_disconnected
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
    @retry_if_disconnected
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
    @retry_if_disconnected
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
