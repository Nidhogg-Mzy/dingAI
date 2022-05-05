import os
import json
import datetime
import unittest
from Leetcode import Leetcode

class LeetcodeTest(unittest.TestCase):
    # TODO: support UTF-8 comparison
    leetcode_data = {
      str(datetime.date.today()): [
        {
          "name": "978. [Removed to avoid UTF-8 error]",
          "id": "longest-turbulent-subarray",
          "link": "https://leetcode-cn.com/problems/longest-turbulent-subarray/",
          "difficulty": "[Removed to avoid UTF-8 error]",
          "description": "dp",
          "participants": ["enor2017"]
        },
        {
          "name": "1305. [Removed to avoid UTF-8 error]",
          "id": "all-elements-in-two-binary-search-trees",
          "link": "https://leetcode-cn.com/problems/all-elements-in-two-binary-search-trees/",
          "difficulty": "[Removed to avoid UTF-8 error]",
          "description": "",
          "participants": []
        }
      ]
    }

    # before each test, load the data and write to ddl_data.json (make sure the file is always the same)
    def setUp(self):
        with open("leetcode-test.json", "w", encoding='utf-8') as f:
            json.dump(self.leetcode_data, f, indent=4, separators=(',', ': '))

    # after each test, delete the ddl_data.json to keep directory clear
    def tearDown(self):
        pass
        # if os.path.exists("leetcode-test.json"):
        #     os.remove("leetcode-test.json")

    def test_load(self):
        leetcode = Leetcode("leetcode-test.json")
        self.assertEqual(self.leetcode_data, leetcode.question_list)

    def test_store(self):
        # correct answer
        with open("leetcode-test-temp.json", "w", encoding='utf-8') as f:
            json.dump(self.leetcode_data, f, indent=4, separators=(',', ': '))
        leetcode = Leetcode("leetcode-test.json")
        leetcode.store_questions()

        self.assertEqual(0, os.system("diff leetcode-test.json leetcode-test-temp.json"))

        if os.path.exists("leetcode-test-temp.json"):
            os.remove("leetcode-test-temp.json")

    # skip the test when there is no chromedriver installed.  TODO: let it run on Github Action
    @unittest.skipUnless(os.path.exists('chromedriver'), "No chrome driver installed.")
    def test_get_question_details(self):
        result = Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lcof')
        answer = {
            'name': '剑指 Offer 03. 数组中重复的数字',
            'id': 'shu-zu-zhong-zhong-fu-de-shu-zi-lcof',
            'link': 'https://leetcode-cn.com/problems/shu-zu-zhong-zhong-fu-de-shu-zi-lcof',
            'difficulty': '简单'
        }
        self.assertEqual(answer, result)

        # non-existing id
        self.assertEqual({}, Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lf'))
        self.assertEqual({}, Leetcode.get_prob_detail_from_id(''))
        self.assertEqual({}, Leetcode.get_prob_detail_from_id('  '))
        self.assertEqual({}, Leetcode.get_prob_detail_from_id('#$!%gb"123"haha'))

    @unittest.skipUnless(os.path.exists('chromedriver'), "No chrome driver installed.")
    def test_user_recent_submission(self):
        # This is hard to test since the users' submission records can change from time to time
        # so we just perform some sanity tests

        result = Leetcode.get_recent_passed_submission('enor2017')
        self.assertFalse(not result)            # not empty check
        self.assertGreater(len(result), 2)      # at least 2 submissions

    @unittest.skip("Change to latest data if you want to test.")
    @unittest.skipUnless(os.path.exists('chromedriver'), "No chrome driver installed.")
    def test_check_finish_problem(self):
        # This is also hard to test, by default we skip this test,
        # when want to test, you should modify the variables below
        self.assertTrue(Leetcode.check_finish_problem('713. 乘积小于 K 的子数组', 'enor2017'))
        self.assertFalse(Leetcode.check_finish_problem('1. 两数之和', 'enor2017'))

        # test invalid problem name
        self.assertFalse(Leetcode.check_finish_problem('haha testing', 'enor2017'))

    def test_query_invalid_command(self):
        leetcode = Leetcode("leetcode-test.json")

        message_parts = ["[dummy]", "leet", "invalid_command"]
        qq = "123456789"
        self.assertTrue("Error" in leetcode.process_query(message_parts, qq))

        message_parts = ["[dummy]", "leet", ""]
        self.assertTrue("Error" in leetcode.process_query(message_parts, qq))

        message_parts = ["[dummy]", "leet", "  "]
        self.assertTrue("Error" in leetcode.process_query(message_parts, qq))

        message_parts = ["[dummy]", "leet", "%5289nd^^\"()"]
        self.assertTrue("Error" in leetcode.process_query(message_parts, qq))

        # Below are program bugs, we should not pass non-leetcode query into this function
        message_parts = ["[dummy]", "haha", " "]
        self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))

        message_parts = ["[dummy]", " "]
        self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))

        message_parts = ["[dummy]"]
        self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))

        message_parts = []
        self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))

        message_parts = None
        self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))

    def test_query_help(self):
        leetcode = Leetcode("leetcode-test.json")
        message_parts = ["[dummy]", "leet", "help"]
        qq = "12345678"
        # check some essential keywords
        result_message = leetcode.process_query(message_parts, qq)
        self.assertTrue("leet help" in result_message)
        self.assertTrue("leet submit" in result_message)
        self.assertTrue("leet insert" in result_message)
        self.assertTrue("leet delete" in result_message)
        self.assertTrue("leet today" in result_message)
        self.assertTrue("leet username" in result_message)
        self.assertTrue("leet register" in result_message)
        # should not contain error
        self.assertFalse("Error" in result_message)

    def test_get_questions_on_date(self):
        # this test the function, not the query
        leetcode = Leetcode("leetcode-test.json")
        answer = [{'name': '978. [Removed to avoid UTF-8 error]',
                   'id': 'longest-turbulent-subarray',
                   'link': 'https://leetcode-cn.com/problems/longest-turbulent-subarray/',
                   'difficulty': '[Removed to avoid UTF-8 error]', 'description': 'dp', 'participants': ['enor2017']},
                  {'name': '1305. [Removed to avoid UTF-8 error]',
                   'id': 'all-elements-in-two-binary-search-trees',
                   'link': 'https://leetcode-cn.com/problems/all-elements-in-two-binary-search-trees/',
                   'difficulty': '[Removed to avoid UTF-8 error]', 'description': '', 'participants': []}]
        # get the questions for today
        self.assertEqual(answer, leetcode.get_question_on_date())
        self.assertEqual(answer, leetcode.get_question_on_date(str(datetime.date.today())))

        # get the questions for a day without questions
        self.assertEqual([], leetcode.get_question_on_date('2000-01-01'))

    def test_query_get_questions_on_date(self):
        leetcode = Leetcode("leetcode-test.json")
        qq = "12345678"

        answer = f"""[TBA]题目列表:
==========
题目名称: 978. [Removed to avoid UTF-8 error]
题目链接: https://leetcode-cn.com/problems/longest-turbulent-subarray/
题目难度: [Removed to avoid UTF-8 error]
已完成名单: ['enor2017']
==========
题目名称: 1305. [Removed to avoid UTF-8 error]
题目链接: https://leetcode-cn.com/problems/all-elements-in-two-binary-search-trees/
题目难度: [Removed to avoid UTF-8 error]
已完成名单: []
"""
        self.assertEqual(answer.replace('[TBA]', '今日'),
                         leetcode.process_query(['dummy', 'leet', 'today'], qq))

        self.assertEqual('[Error] 日期2000-01-01还没有题目哦.',
                         leetcode.process_query(['dummy', 'leet', '2000-01-01'], qq))
        # this will not be passed into date query
        self.assertEqual('[Error] Invalid syntax. Use "leet help" to check usage.',
                         leetcode.process_query(['dummy', 'leet', '84-2'], qq))
        self.assertEqual(answer.replace('[TBA]', str(datetime.date.today()) + '的'),
                         leetcode.process_query(['dummy', 'leet', str(datetime.date.today())], qq))

    def test_query_insert_questions(self):
        pass

    def test_query_insert_questions_invalid(self):
        pass

    def test_query_delete_questions(self):
        pass

    def test_query_delete_questions_invalid(self):
        pass

    def test_query_submit(self):
        pass

    def test_query_submit_invalid(self):
        pass

    # User operations
    def test_register(self):
        pass

    def test_register_invalid(self):
        pass

    def test_get_username(self):
        pass

    def test_get_username_invalid(self):
        pass


if __name__ == '__main__':
    unittest.main()
