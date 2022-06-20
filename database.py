import datetime
import json
from time import sleep
import mysql.connector
from mysql.connector import errorcode


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
    def insert_leetcode(id_: str, name: str, link: str, difficulty: str) -> tuple:
        """
        This method insert leetcode question into table leetcode in database, and
        insert tags into table QuestionTags.

        :param id_: problem id
        :param name: problem name
        :param link: problem link
        :param difficulty: problem difficulty

        :return A tuple [bool, str], 1st position is True if successfully inserted, False if failed.
        The 2nd position is error message if failed.
        """
        try:
            sql_cmd = f'INSERT INTO {DataBase._database}.LeetCode (id, name, link, difficulty) ' \
                       'VALUES (%s, %s, %s, %s)'
            DataBase.cursor.execute(sql_cmd, (id_, name, link, difficulty))
            DataBase.connection.commit()

            return True, ''
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return True, ''     # ok if the question is already in database.
            # for other errors, return as error message
            return False, str(err)

    @staticmethod
    @retry_if_disconnected
    def insert_question_tags(id_: str, tags: list) -> tuple:
        """
        This method insert tags of a certain problem id.

        :param id_: problem id
        :param tags: Tags of the problem, a list of str, cannot be None.

        :return A tuple [bool, str], 1st position is True if successfully inserted, False if failed.
        The 2nd position is error message if failed.
        """
        try:
            for tag in tags:
                sql_cmd = f'INSERT INTO {DataBase._database}.QuestionTags (id, tag) ' \
                           'VALUES (%s, %s)'
                DataBase.cursor.execute(sql_cmd, (id_, tag))
                DataBase.connection.commit()
            return True, ''
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return True, ''     # ok if the tag is already in database.
            # for other errors, return as error message
            return False, str(err)

    @staticmethod
    @retry_if_disconnected
    def delete_leetcode(id_: str, date: str = '') -> tuple:
        if date == '':
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            sql_cmd = f'DELETE FROM {DataBase._database}.StudyOn WHERE id = %s and date = %s'
            DataBase.cursor.execute(sql_cmd, (id_, date))
            DataBase.connection.commit()
            return True, f'成功删除题目: {id_}, 日期为: {date}'
        except mysql.connector.Error as err:
            return False, str(err)

    @staticmethod
    @retry_if_disconnected
    def insert_study_on(id_: str, date: str = '') -> tuple:
        """
        This method insert a new record to the table StudyOn,
        given the problem id and the date to study.

        :param id_: problem id to insert
        :param date: the date to study the problem

        :return A tuple [bool, str], 1st position is True if successfully inserted, False if failed.
        The 2nd position is error message if failed.
        """
        try:
            sql_cmd = f'INSERT INTO {DataBase._database}.StudyOn(date, id) VALUES (%s, %s)'
            if date == '':
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            DataBase.cursor.execute(sql_cmd, (date, id_))
            DataBase.connection.commit()
            return True, ''
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False, f'数据库中已存在id为：{id_}， 日期为{date}的刷题计划'
            elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                return False, f'数据库中不存在id为：{id_}的题目, 请联系管理员处理'
            return False, str(err)

    @staticmethod
    @retry_if_disconnected
    def get_question_on_date(date: str = '') -> list:
        """
        This method get all the question on a specific date

        """
        if date == '':
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        sql_cmd = f'SELECT * FROM {DataBase._database}.LeetCode l, {DataBase._database}.StudyOn s WHERE s.date = %s ' \
                  f'AND l.id = s.id'
        DataBase.cursor.execute(sql_cmd, (date,))
        questions = DataBase.cursor.fetchall()
        toReturn = []
        for q in questions:
            question = {'id': q[0], 'name': q[1], 'link': q[2], 'difficulty': q[3]}
            toReturn.append(question)
        return toReturn

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
        sql_cmd = f'SELECT participant FROM {DataBase._database}.ParticipateIn WHERE date = %s AND id = %s'
        val = (date, problem_id)
        DataBase.cursor.execute(sql_cmd, val)
        participant_object = DataBase.cursor.fetchall()
        participant_list = []
        for p in participant_object:
            participant_list.append(p[0])
        print(participant_list)
        if qq in participant_list:
            return True
        return False

    @staticmethod
    @retry_if_disconnected
    def submit_problem(date: str, problem_id: str, qq: str) -> tuple:
        """
        This function will be called when a user successfully submits the problem.

        :param date The date of given problem
        :param problem_id The unique id of problem, not problem name
        :param qq The qq account of user
        :return True,
        """
        try:
            sql_cmd = f'INSERT INTO {DataBase._database}.ParticipateIn (date, id, participant) VALUES (%s, %s, %s)'
            val = (date, problem_id, qq)
            DataBase.cursor.execute(sql_cmd, val)
            DataBase.connection.commit()
            return True, ''
        except mysql.connector.Error:
            # other possible exception are already handled in leetcode.py
            return False, '数据库发生未知错误，请联系管理员处理'

    @staticmethod
    @retry_if_disconnected
    def get_prob_participant(problem_id: str, date: str = '', username: bool = False) -> list:
        """
        This function get all participants for given problem on given date.

        :param date The date of given problem
        :param problem_id The unique id of problem, not problem name
        :param username True if want to get username instead of QQAccount
        :return A list containing all users (identified by qq) that have submitted the problem
        """
        if date == '':
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if not username:
            sql_cmd = f'SELECT participant FROM {DataBase._database}.ParticipateIn WHERE date = %s AND id = %s'
            DataBase.cursor.execute(sql_cmd, (date, problem_id))
            result = DataBase.cursor.fetchall()
        else:
            sql_cmd = f'SELECT u.username FROM {DataBase._database}.Users u, {DataBase._database}.ParticipateIn p WHERE p.participant = u.QQAccount and p.date = %s and p.id = %s'
            DataBase.cursor.execute(sql_cmd, (date, problem_id))
            result = DataBase.cursor.fetchall()
        toReturn = [r[0] for r in result]
        return toReturn


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
    def select_user(username: str) -> tuple:
        sql_cmd = f'SELECT QQAccount FROM {DataBase._database}.Users WHERE username = %s'
        DataBase.cursor.execute(sql_cmd, (username, ))
        QQAcount = DataBase.cursor.fetchall()
        if not QQAcount:
            return False, ''
        return True, QQAcount[0][0]

    @staticmethod
    @retry_if_disconnected
    def update_user(qq_account: str, username: str) -> None:
        """
        This method updates the leetcode account of the user with qq_account.
        no need to consider the situation when the user does not exist. It is already handled in UserOperation.py
        :param qq_account The qq_account of the user to update
        :param username The new leetcode username of the user
        """
        sql_cmd = f'UPDATE {DataBase._database}.Users SET username = %s WHERE QQAccount = %s'

        DataBase.cursor.execute(sql_cmd, (username, qq_account))
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
    DataBase.init_database()
