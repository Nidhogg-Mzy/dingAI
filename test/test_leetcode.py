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


if __name__ == '__main__':
    unittest.main()
