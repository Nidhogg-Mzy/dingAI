import datetime
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from UserOperation import UserOperation
from time import sleep


class Leetcode:
    """
    Serve as Leetcode API.
    """

    def __init__(self):
        self.filename = 'leetcode.json'
        self.leet_list = []
        self.load_leet_from_file()

    def question_of_today(self) -> dict:
        self.load_leet_from_file()
        today = datetime.date.today()  # current date
        result = self.get_leet(lambda prob: prob['date'] == str(today))
        if not result:
            return {}
        return result[0]

    def load_leet_from_file(self):
        """
        Load leetcode problem list from file, store the result in self.leet_list
        """
        with open(self.filename, "r") as f:
            self.leet_list = json.load(f)  # A list of dict

    def get_leet(self, predicate: lambda ddl: bool) -> list:
        """
        Return a list of leetcode problem that satisfy the predicate
        :param predicate: a function that takes a ddl and returns True or False based on your predicate
        :return: a list of leetcode problem that satisfy the predicate
        """
        return list(filter(predicate, self.leet_list))

    def store_leet(self):
        """
        Store the self.leet_list to file, we don't handle any exception here.
        """
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.leet_list, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    @staticmethod
    def get_recent_passed_submission(username: str, debug=False) -> list:
        """
        Get the recent PASSED submission records for a user, we can only get passed ones.
        :param username: The leetcode username of the user
        :param debug: If True, print debug messages
        :return: A list, each item is ['problem name']
        """
        url = f"https://leetcode-cn.com/u/{username}/"

        # we need to use web-driver to open the webpage
        # The webpage got from requests is not complete
        # use a headless-chrome as webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # fix problems on non-graphics ubuntu server
        options.add_argument('--headless')
        driver = webdriver.Chrome('./chromedriver', options=options)
        driver.get(url)
        sleep(3)  # wait for the webpage to load
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')
        driver.close()
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
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # fix problems on non-graphics ubuntu server
        options.add_argument('--headless')
        driver = webdriver.Chrome('./chromedriver', options=options)
        url = f"https://leetcode-cn.com/problems/{problem_id}"
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')
        driver.close()

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

    def process_query(self, query: list, user_qq: str) -> str:
        """
        Given a list of queries, return the result of the query
        :param query: A list of queries, each query is a list of strings, which is the list of strings where
        after the rev['raw_message'] is split by ' '
        :param user_qq: The user's qq number
        :return: The result of the query
        """

        if (query is None) or (not query) or (len(query) == 1):
            return "[Internal Error] The query is empty."
        if len(query) < 3:
            return "[Error] Invalid syntax. Use \"ddl help\" to check usage."

        if query[1] != "leet":
            return "[Internal Error] Non-leetcode query should not be passed into function process_query."

        if query[2] == 'today':
            question = self.question_of_today()
            if not question:
                return "[Error] No question today."
            else:
                return question['date'] + ":\n" + "今日题目 : " + question['name'] + "\n" + \
                       "题目链接 : " + question['link'] + "\n" + \
                       "难度 : " + question['difficulty'] + "\n" + \
                       "标签 : " + question['description'] + "\n"
        elif query[2] == 'check':
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
            if len(query) == 3:
                return 'leet insert {"date": "enter the date", "name": "enter name here", "id": "enter the id here", ' \
                       '"link": "enter the link here", "difficulty": "enter the difficulty here", ' \
                       '"description": "enter the description here"}'
            leetcode_info = ' '.join(query[3:])
            try:
                res = json.loads(leetcode_info)
                curr_date = res['date']
            except json.JSONDecodeError:
                return "[Error] Invalid syntax. Use \"leet insert\" to check usage."
            if re.search(r"^\d{4}-\d{2}-\d{2}$", curr_date):
                res['participants'] = ''
                self.load_leet_from_file()
                self.leet_list.append(res)
                self.store_leet()
                return 'Inserted successfully!'
            else:
                return '[Error] Invalid Date.'
        elif query[2] == 'help':
            return '''
            [leet today]: 查看今日题目
            [leet check]: 查看是否已完成今日题目(须绑定Leetcode账户)
            [leet insert]: 插入题目
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
