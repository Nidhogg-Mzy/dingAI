import os
import json
import unittest
from Leetcode import Leetcode

class LeetcodeTest(unittest.TestCase):
    # TODO: support UTF-8 comparison
    leetcode_data = {
      "2022-05-01": [
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
        if os.path.exists("leetcode-test.json"):
            os.remove("leetcode-test.json")

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

    def test_get_question_details(self):
        pass

    def test_check_user_finish_question(self):
        pass

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

    def test_query_get_questions_on_date(self):
        pass

    def test_query_get_questions_on_date_invalid(self):
        pass

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
