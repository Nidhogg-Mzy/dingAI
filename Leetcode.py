import datetime
import re
from time import sleep
from bs4 import BeautifulSoup
from UserOperation import UserOperation
from WebDriver import WebDriver
from database import DataBase


class Leetcode:
    """
    Serve as Leetcode API.
    This file should keep a list that records all the
    """

    """
    Store today's question in question_list as a list, and each question in form:
    {
            "id": "longest-turbulent-subarray",
            "name": "978. 最长湍流子数组",
            "link": "https://leetcode.cn/problems/longest-turbulent-subarray/",
            "difficulty": "中等",
    }
    """
    question_list = DataBase.get_question_on_date()

    ####################
    # Helper Functions #
    ####################

    @staticmethod
    def get_recent_passed_submission(username: str, debug=False) -> list:
        """
        Get the recent PASSED submission records for a user, we can only get passed ones.
        :param username: The leetcode username of the user
        :param debug: If True, print debug messages
        :return: A list, each item is ['problem name']
        """
        url = f"https://leetcode.cn/u/{username}/"
        driver = WebDriver.get_driver()
        driver.get(url)
        # continue to load webpage until the certain span tag is found
        # set timeout to 5 seconds
        passed_lists = None
        soup = None
        timeout_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=5)
        while datetime.datetime.now() < timeout_timestamp:
            page = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(page, 'html.parser')
            passed_lists = soup.find_all('span', class_='text-label-1 dark:text-dark-label-1 font-medium line-clamp-1')
            if passed_lists is None or not passed_lists:
                sleep(0.25)  # not found, continue to wait
                continue
            break  # already found, break the loop

        if debug:
            print(soup.prettify())

        passed_problems = []
        for passed in passed_lists:
            problem_name = passed.text
            if problem_name not in passed_problems:
                passed_problems.append(problem_name)
                if debug:
                    print(f"Passed: {problem_name}, added to list")

        if debug:
            print(passed_problems)
            print(f"\n\n=====\ntotal length: {len(passed_problems)}")
        return passed_problems

    @staticmethod
    def get_prob_detail_from_id(problem_id: str) -> dict:
        """
        Given problem id (english id in problem url), return the problem details
        :param problem_id: Given problem id to check
        :return: A dict containing the problem detail, {"name": "<problem name>", "id": "<problem id>",
        "link": "<problem link>", "difficulty": "<problem difficulty>"}.
        Return {} if the problem is not found.
        """
        # Actually it's possible to add extra slashes before/after problem_id
        # here we clean it for simplicity
        problem_id = problem_id.strip('/')
        # set up chrome driver
        driver = WebDriver.get_driver()
        url = f"https://leetcode.cn/problems/{problem_id}"
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # continue to load webpage until the certain div of problem spec is found
        # set timeout to 5 seconds
        problem_spec = None
        timeout_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=5)
        while datetime.datetime.now() < timeout_timestamp:
            page = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(page, 'html.parser')

            problem_spec = soup.find('div', class_="description__2b0C")
            if problem_spec is None or not problem_spec:
                # continue to wait
                sleep(0.25)
                continue
            break  # else, already retrieved valid problem_spec, break loop
        # if after timeout, we still didn't get the problem spec, return empty dict
        if problem_spec is None or not problem_spec:
            return {}

        # filter problem title
        def filter_prob_title(tag):
            return tag.name == 'h4' and tag.has_attr('data-cypress')

        problem_title = problem_spec.find(filter_prob_title)

        # filter problem difficulty
        def filter_prob_difficulty(tag):
            return tag.name == 'span' and tag.has_attr('data-degree')

        problem_difficulty = problem_spec.find(filter_prob_difficulty)

        # return the details got
        if problem_title is None or problem_difficulty is None:
            return {}
        return {"name": problem_title.text, "id": problem_id,
                "link": url, "difficulty": problem_difficulty.text}

    @staticmethod
    def check_finish_problem(problem_name: str, username: str, debug: bool = False) -> bool:
        """
        Given problem name (whole name, not id), check if the user has passed the problem.
        :param problem_name: Given full problem name to check, not problem id
        :param username: The leetcode username of the user
        :param debug: If True, print the debug info
        :return: True, if the user passed the problem
        """
        passed_record = Leetcode.get_recent_passed_submission(username=username, debug=debug)
        return problem_name in passed_record

    @staticmethod
    def display_questions(question_list: list, date: str = '') -> str:
        """
        Given a list of questions, display them in a readable format.
        :param question_list: A list of questions, each question is a dict.
        :param date: The date of the questions, if not given, will use today's date
        :return: A string containing the question list in readable format
        """
        output = ""
        if date == '':
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        for question in question_list:
            participants = DataBase.get_prob_participant(question["id"], date, username = True)
            output += (
                f"{'=' * 10}\n"
                f"题目名称: {question['name']}\n"
                f"题目链接: {question['link']}\n"
                f"题目难度: {question['difficulty']}\n"
                f"已完成名单: {participants}\n")
        return output

    @staticmethod
    def check_valid_date(date: str) -> bool:
        """
        This function checks if the input date is a valid date, in format YYYY-MM-DD.

        :param date: the given date to check
        :return True if valid, False otherwise
        """
        return re.search(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", date) is not None

    ######################################
    # Main Function for Query Processing #
    ######################################

    # pylint: disable=too-many-branches
    @staticmethod
    def process_query(query: list, user_qq: str) -> str:
        """
        Given a query and the user that performed the query, return the result of the query
        :param query: A query, which is a list of strings
        :param user_qq: The user's qq number who performed the query
        :return: The result of the query to be sent to the user
        """

        if (query is None) or (not query) or (len(query) < 2):
            return "[Internal Error] The query is empty."

        if query[1] != "leet":
            return "[Internal Error] Non-leetcode query should not be passed into function process_query."

        if len(query) < 3:
            return "[Error] Invalid syntax. Use \"leet help\" to check usage."

        if query[2] == 'today':
            if not Leetcode.question_list:
                return "[Error] 今天还没有题目哦."
            return f"今日题目列表:\n{Leetcode.display_questions(Leetcode.question_list)}"
        if re.search(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", query[2]):
            questions = DataBase.get_question_on_date(query[2])
            if not questions:
                return f"[Error] 日期{query[2]}还没有题目哦."
            return f"{query[2]}的题目列表:\n{Leetcode.display_questions(questions, query[2])}"
        if query[2] == 'status':
            # the user must have been registered before using this command
            if len(query) > 3:
                return "[Error] Invalid syntax. Use \"leet help\" to check usage."
            status_, username_ = UserOperation.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>'

            questions_status = {}  # {('question id', 'question name'): true/false}
            # this query will not retrieve passed records from leetcode website, we simply
            # retrieve the records in our database. User should use 'submit' to invoke a check.
            for q in Leetcode.question_list:
                questions_status[(q['id'], q['name'])] = username_ in DataBase.get_prob_participant(q['id'], str(datetime.date.today()), True)

            to_return = "今日题目你的完成状态: \n"
            for (k, v) in questions_status.items():
                to_return += f"{k[0]} {k[1]}: {'已通过!' if v else '还没通过哦.'}\n"
            to_return += "如果有记录错误, 尝试先通过leet submit提交一下哦!"
            return to_return

        if query[2] == 'submit':
            # user must have been registered before using this command
            status_, username_ = UserOperation.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>'

            # pylint: disable=no-else-return
            today_date = str(datetime.date.today())
            if len(query) == 3:
                # submit all the questions today
                to_return = "提交今日所有题目:\n"
                today_questions = Leetcode.question_list
                # no questions today:
                if not today_questions:
                    return "Ahh, 今天还没有题目哦 >.<"
                for q in today_questions:
                    result = Leetcode.submit_question(today_date, q['name'], str(user_qq), username_)
                    to_return += f"题目[{q['name']}]: {result}\n"
                return to_return[:-1]       # remove \n
            else:
                # submit a specific question
                # check if the name is valid
                question_name = ' '.join(query[3:])     # question name received
                if question_name not in [q['name'] for q in Leetcode.question_list]:
                    return f"[Error] 今天没有名为'{question_name}'的题目哦!"

                # submit the question
                result = Leetcode.submit_question(today_date, question_name, str(user_qq), username_)
                return f"题目[{question_name}]: {result}"

        # register: match the qq account with leetcode username,
        # so user don't need to provide username when query
        if query[2] == 'register':
            # if query is invalid
            if len(query) != 4:
                return '[Error]正确食用方法: leet register <your leetcode username>'

            _, msg_ = UserOperation.register(str(user_qq), query[3])
            return msg_
        # check username, for already registered users
        if query[2] == 'username':
            # if query is invalid
            if len(query) != 3:
                return '[Error]正确食用方法: leet username'
            status_, username_ = UserOperation.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode用户名诶，要不要试试 leet register <your leetcode username>'
            return f'您已绑定LeetCode的用户名是: {username_}'
        if query[2] == 'insert':
            if len(query) < 5 or (len(query) > 2 and query[3] == 'help'):  # tag can be empty
                return '[Error] 请使用leet insert <date> <question id> <tags> 插入题目, 其中<date>格式为YYYY-MM-DD, ' \
                       '多个tag用空格分隔, 没有tag请留空.'
            date_received = query[3]
            question_id = query[4]
            tags = query[5:]

            # check if date is valid
            if not Leetcode.check_valid_date(date_received):
                return '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'

            return Leetcode.insert_question(question_id, tags, date_received)

        if query[2] == 'delete':
            if len(query) != 5 or (len(query) > 2 and query[3] == 'help'):
                return '[Error] 请使用leet delete <date> <question id> 删除题目, 其中<date>格式为YYYY-MM-DD'
            date_received = query[3]
            question_id = query[4]

            # check if date is valid
            if not re.search(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", date_received):
                return '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
            # check if the question exists
            if question_id not in [q['id'] for q in Leetcode.question_list]:
                return f'[Error] 日期为"{date_received}"的题目中没有id为"{question_id}"的题目.'

            # delete the question
            result = DataBase.delete_leetcode(question_id, date_received)
            if result[0]:
                Leetcode.question_list = DataBase.get_question_on_date()
                return result[1]
            else:
                return result[1]

        if query[2] == 'help':
            return 'Leetcode 相关指令: \n' \
                   '[leet today]: 查看今日题目\n' \
                   '[leet <date>]: 查看指定日期的题目, 日期为YYYY-MM-DD\n' \
                   '[leet status]: 查看今日题目完成进度(须绑定Leetcode账户)\n' \
                   '[leet submit]: 提交今日所有题目(不必全部完成, 须绑定Leetcode账户)\n' \
                   '[leet submit <question_name>]: 提交今日指定题目(须绑定Leetcode账户)\n' \
                   '[leet insert <date> <question id> <tags>]: 在给定日期插入题目\n' \
                   '[leet delete <date> <question id>]: 在给定日期删除题目\n' \
                   '[leet register]: 绑定Leetcode账户\n' \
                   '[leet username]: 查看已绑定的Leetcode账户\n' \
                   '[leet help]: 查看此帮助'

        # invalid command
        return "[Error] Invalid syntax. Use \"leet help\" to check usage."

    ####################
    # Function Modules #
    ####################

    @staticmethod
    def insert_question(question_id: str, tags: list, date: str) -> str:
        """
        process the query to insert question on certain date.

        :param question_id: problem id
        :param tags: A list of tags. Can be empty, not cannot be None
        :param date: on which date to insert, must be a valid date

        :return The result message to display to user.
        """
        # get question details
        question_details = Leetcode.get_prob_detail_from_id(question_id)
        if not question_details:
            return f'[Error] 找不到id为"{question_id}"的题目. 如果你认为这是一个错误，请联系管理员.'

        # insert problem to database
        result1 = DataBase.insert_leetcode(question_id, question_details['name'], question_details['link'],
                                           question_details['difficulty'])
        if not result1[0]:
            return result1[1]       # return error message if failure

        # insert question tags
        result2 = DataBase.insert_question_tags(question_id, tags)
        if not result2[0]:
            return result2[1]       # return error message if failure

        # insert study plan
        result3 = DataBase.insert_study_on(question_id, date)
        if not result3[0]:
            return result3[1]       # return error message if failure

        return f'成功插入题目: {question_details["name"]}, 日期为: {date}'

    @staticmethod
    def submit_question(question_date: str, question_name: str, qq: str, username: str) -> str:
        """
        Perform a user's submission of given question on specific date. We assume the parameters are valid.

        :param question_date: date of the question
        :param question_name: name of the question
        :param qq: the qq account of the user           TODO: can we only use one?
        :param username: the leetcode username of the user

        :return: Result message to display to users
        """
        # get the object of that question in question_list
        question_obj = None
        for q in Leetcode.question_list:
            if q['name'] == question_name:
                question_obj = q
                break
        if question_obj is None:
            return "[Internal Error] 无法找到题目"    # this should not happen, since we ensured valid parameters

        # check if user has already submitted the question  TODO: retrieve from cache
        participants = DataBase.get_prob_participant(question_obj['id'], username=True)
        if username in participants:
            return "您已提交过此题目"

        # check if user finished the question
        status = Leetcode.check_finish_problem(question_name, username)
        if not status:
            return "您没有完成此题目"

        # update participant record in database
        result = DataBase.submit_problem(question_date, question_obj['id'], qq)
        if not result:
            return "[Internal Error] 用户通过题目，但无法将通过信息同步到数据库"

        return "成功提交此题目!"

    @staticmethod
    def update_question_list():
        """
        Update the question list every 5 min.
        :return: None
        """
        # get the question list from leetcode
        while True:
            # get current time in UTC+8
            curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            # check if it is midnight
            if curr_time.hour == 0 and curr_time.minute == 0:
                Leetcode.question_list = DataBase.get_question_on_date(curr_time.strftime('%Y-%m-%d'))
                sleep(20)  # allow some buffer time.


if __name__ == '__main__':
    pass
