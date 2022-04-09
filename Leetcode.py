import datetime
import json
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from UserOperation import UserOperation


class Leetcode:
    """
    Serve as Leetcode API.
    """

    def __init__(self):
        self.recent_submission = None
        self.filename = 'leetcode.json'
        self.leet_list = []

    def question_of_today(self) -> dict:
        self.load_leet_from_file()
        for i in range(len(self.leet_list)):
            date = self.leet_list[i]['date']
            question_year = date.split('-')[0]
            question_month = date.split('-')[1]
            question_day = date.split('-')[2]
            now = datetime.datetime.now()  # current date and time
            curr_year = now.strftime("%Y")
            curr_month = now.strftime("%m")
            curr_day = now.strftime("%d")
            if (curr_year == question_year) and (curr_month == question_month) and (curr_day == question_day):
                return self.leet_list[i]
        return None

    def load_leet_from_file(self):
        """
        Load ddl list from file, store the result in self.ddl_list
        """
        with open(self.filename, "r") as f:
            self.leet_list = json.load(f)  # A list of dict

    def get_leet(self, predicate: lambda ddl: bool) -> list:
        """
        Return a list of ddl that satisfy the predicate
        :param predicate: a function that takes a ddl and returns True or False based on your predicate
        :return: a list of ddl that satisfy the predicate
        """
        return list(filter(predicate, self.leet_list))

    def store_leet(self):
        """
        Store the self.ddl_list to file, we don't handle any exception here.
        """
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.leet_list, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    def get_recent_passed_submission(self, username: str, debug=False, force_refresh=False) -> list:
        """
        Get the recent PASSED submission records for a user, only get passed ones.
        :param debug: If True, print debug messages
        :param force_refresh: If True, force refresh the result, do not read from cache
        :return: A list, each item is ['problem name', 'problem id', 'language', 'time']
        """
        # check if the recent submission is cached
        if (not force_refresh) and (self.recent_submission is not None):
            return self.recent_submission

        url = f"https://leetcode-cn.com/u/{username}/"

        # we need to use web-driver to open the webpage
        # The webpage got from requests is not complete
        # use a headless-chrome as webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # fix problems on non-graphics ubuntu server
        options.add_argument('--headless')
        driver = webdriver.Chrome('./chromedriver', options=options)
        driver.get(url)
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')
        driver.close()
        if debug:
            print(soup.prettify())

        sub_lists = soup.find_all('div', class_='css-ueaw7d-StackRow ekb1c6d5')
        submission_details = []
        for sub in sub_lists:
            problem = sub.find('a', class_="css-1e9rbo3-Link e14iayf26")
            prob_name = problem.text
            prob_id = problem['href'].split('/')[-2]

            lang = sub.find('span', class_="css-1n3niua-Lang e14iayf210").text
            result = sub.find('span', class_="e14iayf29 css-1ew5sfu-BasicTag-StyledTag e4dtce60")
            # if result is None, this submission is not passed
            if result is None:
                continue
            # result = result.span.text
            time = sub.find('div', class_="css-ex16d6-Timestamp e14iayf25").text

            this_detail = [prob_name, prob_id, lang, time]
            if debug:
                print(this_detail)
            submission_details.append(this_detail)
        # store the result as cache
        self.recent_submission = submission_details
        return submission_details

    def check_finish_problem(self, problem_id: str, username: str, force_refresh=False) -> list:
        """
        Given problem id (english id in problem url), check if the user has passed the problem.
        Return a list, containing all languages that the user used to pass the problem.
        :param problem_id: Given problem id to check
        :param force_refresh: If True, force refresh the result, do not read from cache
        :return: A list of languages that the user used to pass the problem
        """
        passed_record = self.get_recent_passed_submission(username=username, force_refresh=force_refresh)
        result_list = []
        for record in passed_record:
            if record[1] == problem_id:
                result_list.append(record[2])
        return result_list

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
            if question is None:
                return "[Error] No question today."
            else :
                return question['date'] + ":\n" + "今日题目 : " + question['name'] + "\n" + \
                       "题目链接 : " + question['link'] + "\n" + \
                       "难度 : " + question['difficulty'] + "\n" + \
                       "标签 : " + question['description'] + "\n"
        elif query[2] == 'check':
            # if user name is not provided, the user must have been registered, otherwise, report error
            if len(query) < 3:
                user_op = UserOperation()
                status_, username_ = user_op.get_leetcode(str(user_qq))
                if not status_:
                    return '我还不知道您的LeetCode账户名哦，试试 register <your leetcode username>, 或者在check 后面加上你要查找的用户名哦!'
                username = username_
            # otherwise, we should get user name from user input
            else:
                username = query[2]
            leetcode = Leetcode()
            res = leetcode.check_finish_problem('binary-search', username)
            if not res:
                return '你怎么没写完啊？坏孩子！'
            else:
                self.load_leet_from_file()
                question = self.question_of_today()
                question['participants'] += username + ' '
                return f'You have passed this problem in the following languages: {res}'
        # register: match the qq account with leetcode username,
        # so user don't need to provide username when query
        elif query[2] == 'register':
            # if username is not provided
            if len(query) < 4:
                return '正确食用方法: register <your leetcode username>'
            else:
                user_op = UserOperation()
                _, msg_ = user_op.register(str(user_qq), query[3])
                return msg_
        # check username, for already registered users
        elif query[2] == 'username':
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(user_qq))
            if not status_:
                return '我还不知道您的LeetCode用户名诶，要不要试试 register <your leetcode username>'
            else:
                return f'您已绑定LeetCode的用户名是: {username_}'
        elif query[2] == 'insert':
            if len(query) == 3:
                return 'leet insert {"date": "enter the date", "name": "enter name here", "id": "enter the id here", ' \
                       '"link": "enter the link here", "difficulty": "enter the difficulty here", ' \
                       '"description": "enter the description here"}'
            Leetcode_info = ''
            for i in range(3, len(query)):
                Leetcode_info += query[i] + ' '
            try:
                res = json.loads(Leetcode_info)
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
        else:
            return "[Error] Invalid syntax. Use \"leet help\" to check usage."
