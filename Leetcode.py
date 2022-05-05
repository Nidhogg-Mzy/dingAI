import datetime
import json
import re
from time import sleep
from bs4 import BeautifulSoup
from UserOperation import UserOperation
from WebDriver import WebDriver


class Leetcode:
    """
    Serve as Leetcode API.
    """

    def __init__(self, filename="leetcode.json"):
        self.filename = filename
        self.question_list = {}  # key is date, value is a list of questions (dicts) on that date
        self.load_questions_from_file()

    def get_question_on_date(self, date: str = None) -> list:
        """
        Return a list of problems for a given date, if there is no problem, return an empty list.
        :param date: The date of the question, format: YYYY-MM-DD. If not given, default to today.
        """
        if date is None:
            date = str(datetime.date.today())  # current date
        return self.question_list[date] if date in self.question_list else []

    def load_questions_from_file(self):
        """
        Load leetcode problem list from file, store the result in self.problem_list
        """
        with open(self.filename, "r", encoding='utf-8') as f:
            self.question_list = json.load(f)  # A list of questions, each question is a dict

    def store_questions(self):
        """
        Store the self.question_list to file, assuming the file is always available.
        """
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.question_list, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    @staticmethod
    def get_recent_passed_submission(username: str, debug=False) -> list:
        """
        Get the recent PASSED submission records for a user, we can only get passed ones.
        :param username: The leetcode username of the user
        :param debug: If True, print debug messages
        :return: A list, each item is ['problem name']
        """
        url = f"https://leetcode-cn.com/u/{username}/"
        driver = WebDriver.get_driver()
        driver.get(url)
        sleep(2)  # wait for the webpage to load
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')

        if debug:
            print(soup.prettify())

        passed_lists = soup.find_all('span', class_='text-label-1 dark:text-dark-label-1 font-medium line-clamp-1')
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
        # set up chrome driver
        driver = WebDriver.get_driver()
        url = f"https://leetcode-cn.com/problems/{problem_id}"
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')

        # get the whole div of problem spec
        problem_spec = soup.find('div', class_="description__2b0C")
        # if not found, this id is invalid, or the crawler is down
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
    def display_questions(question_list: list) -> str:
        """
        Given a list of questions, display them in a readable format.
        :param question_list: A list of questions, each question is a dict.
        :return: A string containing the question list in readable format
        """
        output = ""
        for question in question_list:
            output += (
                f"{'=' * 10}\n"
                f"题目名称: {question['name']}\n"
                f"题目链接: {question['link']}\n"
                f"题目难度: {question['difficulty']}\n"
                f"已完成名单: {question['participants']}\n")
        return output

    def process_query(self, query: list, user_qq: str) -> str:
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
            questions = self.get_question_on_date()
            if not questions:
                return "[Error] 今天还没有题目哦."
            return f"今日题目列表:\n{Leetcode.display_questions(questions)}"
        elif re.search(r"^\d{4}-\d{2}-\d{2}$", query[2]):
            questions = self.get_question_on_date(query[2])
            if not questions:
                return f"[Error] 日期{query[2]}还没有题目哦."
            return f"{query[2]}的题目列表:\n{Leetcode.display_questions(questions)}"
        elif query[2] == 'status':
            # the user must have been registered before using this command
            if len(query) > 3:
                return "[Error] Invalid syntax. Use \"leet help\" to check usage."
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>'

            questions_today = self.get_question_on_date()
            questions_status = {}    # {('question id', 'question name'): true/false}
            # this query will not retrieve passed records from leetcode website, we simply
            # retrieve the records in our database. User should use 'submit' to invoke a check.
            for q in questions_today:
                questions_status[(q['id'], q['name'])] = username_ in q['participants']

            to_return = "今日题目你的完成状态: \n"
            for (k, v) in questions_status.items():
                to_return += f"{k[0]} {k[1]}: {'已通过!' if v else '还没通过哦.'}\n"
            to_return += "如果有记录错误, 尝试先通过leet submit提交一下哦!"
            return to_return

        elif query[2] == 'submit':
            if not 3 <= len(query) <= 4:
                return "[Error] Invalid syntax. Use \"leet help\" to check usage."

            # user must have been registered before using this command
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>'

            if len(query) == 3:
                # submit all the questions today
                to_return = "提交今日所有题目:\n"
                today_questions = self.get_question_on_date()
                for q in today_questions:
                    curr_status = self.submit_question(datetime.date.today(), q['id'], username_)
                    if curr_status:
                        to_return += f"{q['id']} {q['name']}: 您已成功提交!\n"
                    else:
                        to_return += f"{q['id']} {q['name']}: 您好像还没有完成这道题.\n"
                return to_return
            else:
                # submit a specific question
                # check if the id is valid
                today_questions = self.get_question_on_date()
                question_id = query[3]  # question id received
                if question_id not in [q['id'] for q in today_questions]:
                    return f"[Error] 今天没有id为{question_id}的题目哦!"

                # submit the question
                if self.submit_question(datetime.date.today(), question_id, username_):
                    return f"提交题目 {question_id} 成功!"
                return f"您好像还没有完成题目 {question_id} 哦."

        # register: match the qq account with leetcode username,
        # so user don't need to provide username when query
        elif query[2] == 'register':
            # if username is not provided
            if len(query) < 4:
                return '正确食用方法: leet register <your leetcode username>'

            user_op = UserOperation()
            _, msg_ = user_op.register(str(user_qq), query[3])
            return msg_
        # check username, for already registered users
        elif query[2] == 'username':
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode用户名诶，要不要试试 leet register <your leetcode username>'
            return f'您已绑定LeetCode的用户名是: {username_}'
        elif query[2] == 'insert':
            if len(query) < 5 or (len(query) > 2 and query[3] == 'help'):  # tag can be empty
                return '[Error] 请使用leet insert <date> <question id> <tags> 插入题目, 其中<date>格式为YYYY-MM-DD, ' \
                       '多个tag用空格分隔, 没有tag请留空.'
            date_received = query[3]
            question_id = query[4]
            question_tags = ','.join(query[5:])

            # check if date is valid
            if not re.search(r"^\d{4}-\d{2}-\d{2}$", date_received):
                return '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
            # get question details
            question_details = self.get_prob_detail_from_id(question_id)
            if not question_details:
                return f'[Error] 找不到id为"{question_id}"的题目. 如果你认为这是一个错误，请联系管理员.'

            # store the question
            question_json = {
                'name': question_details['name'],
                'id': question_id,
                'link': question_details['link'],
                'difficulty': question_details['difficulty'],
                'description': question_tags,
                'participants': []
            }
            if date_received not in self.question_list[date_received]:
                self.question_list[date_received] = [question_json]
            else:
                self.question_list[date_received].append(question_json)

            # store the question in database
            self.store_questions()
            return f'成功插入题目: {question_details["name"]}, 日期为: {date_received}'

        elif query[2] == 'delete':
            if len(query) < 4 or (len(query) > 2 and query[3] == 'help'):
                return '[Error] 请使用leet insert <date> <question id> 删除题目, 其中<date>格式为YYYY-MM-DD, '
            date_received = query[3]
            question_id = query[4]

            # check if date is valid
            if not re.search(r"^\d{4}-\d{2}-\d{2}$", date_received):
                return '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
            # check if the question exists
            questions = [x["id"] for x in self.get_question_on_date(date_received)]
            if question_id not in questions:
                return f'[Error] 日期为"{date_received}"的题目中没有id为"{question_id}"的题目.'

            # delete the question
            self.question_list[date_received] = [x for x in self.question_list[date_received] if x["id"] != question_id]
            self.store_questions()
            return f'成功删除题目: {question_id}, 日期为: {date_received}'

        elif query[2] == 'help':
            return '''
            [leet today]: 查看今日题目
            [leet <date>]: 查看指定日期的题目, 日期为YYYY-MM-DD
            [leet status]: 查看今日题目完成进度(须绑定Leetcode账户)
            [leet submit]: 提交今日所有题目(不必全部完成, 须绑定Leetcode账户)
            [leet submit <question_id>]: 提交今日指定id的题目(须绑定Leetcode账户)
            [leet insert <date> <question id> <tags>]: 在给定日期插入题目
            [leet delete <date> <question id>]: 在给定日期删除题目
            [leet register]: 绑定Leetcode账户
            [leet username]: 查看已绑定的Leetcode账户
            [leet help]: 查看此帮助
            '''
        else:
            return "[Error] Invalid syntax. Use \"leet help\" to check usage."

    def submit_question(self, question_date: str, question_id: str, username: str) -> bool:
        """
        Perform a user's submission of given question on specific date. We assume the parameters are valid.
        :param question_date: date of the question
        :param question_id: id of the question
        :param username: the username of leetcode account
        :return: True if the user have finished the question, False otherwise
        """
        # check if user has already submitted the question
        if username in self.question_list[question_date][question_id]['participants']:
            return True

        # check if user finished the question
        status = self.check_finish_problem(question_id, username)
        if status:
            self.question_list[question_date][question_id]['participants'].append(username)
            self.store_questions()
            return True
        return False


if __name__ == '__main__':
    pass
