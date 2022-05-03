import datetime
import json
import re
from bs4 import BeautifulSoup
from UserOperation import UserOperation
from time import sleep
from WebDriver import WebDriver


class Leetcode:
    """
    Serve as Leetcode API.
    """

    def __init__(self, filename="leetcode.json"):
        self.filename = filename
        self.question_list = {}  # key is date, value is a list of questions (dicts) on that date
        self.load_questions_from_file()

    def get_question_today(self) -> list:
        """
        Return a list of problems for today, if there is no problem for today, return an empty list.
        """
        today = datetime.date.today()  # current date
        return self.problem_list[today] if today in self.problem_list else []

    def load_questions_from_file(self):
        """
        Load leetcode problem list from file, store the result in self.problem_list
        """
        with open(self.filename, "r") as f:
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
        else:
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
            output += f"""
            {'=' * 10}
            题目名称: {question['name']}
            题目链接: {question['link']}
            题目难度: {question['difficulty']}
            已完成名单: {question['participants']}
            """
        return output

    def process_query(self, query: list, user_qq: str) -> str:
        """
        Given a query and the user that performed the query, return the result of the query
        :param query: A query, which is a list of strings
        :param user_qq: The user's qq number who performed the query
        :return: The result of the query to be sent to the user
        """

        if (query is None) or (not query) or (len(query) == 1):
            return "[Internal Error] The query is empty."
        if len(query) < 3:
            return "[Error] Invalid syntax. Use \"leet help\" to check usage."

        if query[1] != "leet":
            return "[Internal Error] Non-leetcode query should not be passed into function process_query."

        if query[2] == 'today':
            question = self.get_question_today()
            if not question:
                return "[Error] No question today."
            else:
                return f"今日题目列表:\n{Leetcode.display_questions(question)}"
        elif query[2] == 'status':
            # the user must have been registered before using this command
            if len(query) > 3:
                return "[Error] Invalid syntax. Use \"leet help\" to check usage."
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>'
            question_today = self.question_of_today()
            res = Leetcode.check_finish_problem(question_today['id'], username_)
            if not res:
                return '你怎么没写完啊？坏孩子！'
            else:
                question_today['participants'].append(username_)
                self.store_leet()
                return f'wow! 你使用了这些语言通过这道题: {res}'
        elif query[2] == 'submit':
            pass    # TODO
        # register: match the qq account with leetcode username,
        # so user don't need to provide username when query
        elif query[2] == 'register':
            # if username is not provided
            if len(query) < 4:
                return '正确食用方法: leet register <your leetcode username>'
            else:
                user_op = UserOperation()
                _, msg_ = user_op.register(str(user_qq), query[3])
                return msg_
        # check username, for already registered users
        elif query[2] == 'username':
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode用户名诶，要不要试试 leet register <your leetcode username>'
            else:
                return f'您已绑定LeetCode的用户名是: {username_}'
        elif query[2] == 'insert':
            if len(query) < 5:  # tag can be empty
                return '[Error] 请使用leet insert <date> <question id> <tags> 插入题目, 其中<date>格式为YYYY-MM-DD, ' \
                       '多个tag用空格分隔, 没有tag请留空.'
            date_received = query[3]
            question_id = query[4]
            question_tags = ','.join(query[5:])

            # check if date is valid
            if not re.search(r"^\d{4}-\d{2}-\d{2}$", date_received):
                return '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
            # get question details
            question_details = self.get_question_details(question_id)
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

            return f'成功插入题目: {question_name}, 日期为: {date_received}'

        elif query[2] == 'help':
            return '''
            [leet today]: 查看今日题目
            [leet status]: 查看今日题目完成进度(须绑定Leetcode账户)
            [leet submit]: 提交今日所有题目(不必全部完成, 须绑定Leetcode账户)
            [leet insert]: 在给定日期插入题目
            [leet register]: 绑定Leetcode账户
            [leet username]: 查看已绑定的Leetcode账户
            [leet help]: 查看此帮助
            '''
        else:
            return "[Error] Invalid syntax. Use \"leet help\" to check usage."


if __name__ == '__main__':
    # print(Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lcof'))
    # print(Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lf'))

    print(Leetcode.check_finish_problem('190. 颠倒二进制位', 'enor2017', debug=False))
    print(Leetcode.check_finish_problem('1. 两数之和', 'enor2017', debug=False))
