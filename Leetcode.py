from bs4 import BeautifulSoup
from selenium import webdriver


class Leetcode:
    """
    Serve as Leetcode API.
    """

    def __init__(self, username: str):
        self.username = username
        self.recent_submission = None

    def get_recent_passed_submission(self, debug=False, force_refresh=False) -> list:
        """
        Get the recent PASSED submission records for a user, only get passed ones.
        :param debug: If True, print debug messages
        :param force_refresh: If True, force refresh the result, do not read from cache
        :return: A list, each item is ['problem name', 'problem id', 'language', 'time']
        """
        # check if the recent submission is cached
        if (not force_refresh) and (self.recent_submission is not None):
            return self.recent_submission

        url = f"https://leetcode-cn.com/u/{self.username}/"

        # we need to use web-driver to open the webpage
        # The webpage got from requests is not complete
        # use a headless-chrome as webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')    # fix problems on non-graphics ubuntu server
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

    def check_finish_problem(self, problem_id: str, force_refresh=False) -> list:
        """
        Given problem id (english id in problem url), check if the user has passed the problem.
        Return a list, containing all languages that the user used to pass the problem.
        :param problem_id: Given problem id to check
        :param force_refresh: If True, force refresh the result, do not read from cache
        :return: A list of languages that the user used to pass the problem
        """
        passed_record = self.get_recent_passed_submission(force_refresh=force_refresh)
        result_list = []
        for record in passed_record:
            if record[1] == problem_id:
                result_list.append(record[2])
        return result_list


if __name__ == "__main__":
    leetcode = Leetcode('nidhogg-mzy')
    # leetcode.get_recent_passed_submission()

    # test check finish problem
    res = leetcode.check_finish_problem('binary-search')
    if not res:
        print('You have not passed this problem yet.')
    else:
        print(f'You have passed this problem in the following languages: {res}')

    # Test force_refresh, check if driver could open more than 1 windows
    res = leetcode.check_finish_problem('yuan-quan-zhong-zui-hou-sheng-xia-de-shu-zi-lcof', force_refresh=True)
    if not res:
        print('You have not passed this problem yet.')
    else:
        print(f'You have passed this problem in the following languages: {res}')

    res = leetcode.check_finish_problem('hahaha')
    if not res:
        print('You have not passed this problem yet.')
    else:
        print(f'You have passed this problem in the following languages: {res}')
