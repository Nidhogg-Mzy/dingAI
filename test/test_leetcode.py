## temporarily disable the test, as it is database-free version
# import os
# import json
# import datetime
# import unittest
# import UserOperation    # for delete user interface
# from Leetcode import Leetcode
# from WebDriver import WebDriver, WebDriverCannotFoundException
#
#
# def check_exists_chrome_driver():
#     """
#     This function checks it the chrome driver exists, by trying to initialize a driver
#     """
#     # if already initialized, return available
#     if WebDriver.driver is not None:
#         return True
#     try:
#         _ = WebDriver.new_driver()
#     except WebDriverCannotFoundException:
#         return False
#     return True
#
# # pylint: disable=too-many-public-methods
# class LeetcodeTest(unittest.TestCase):
#     # TODO: support UTF-8 comparison
#     leetcode_data = {
#       str(datetime.date.today()): [
#         {
#           "name": "978. [Removed to avoid UTF-8 error]",
#           "id": "longest-turbulent-subarray",
#           "link": "https://leetcode.cn/problems/longest-turbulent-subarray/",
#           "difficulty": "[Removed to avoid UTF-8 error]",
#           "description": "dp",
#           "participants": ["enor2017"]
#         },
#         {
#           "name": "1305. [Removed to avoid UTF-8 error]",
#           "id": "all-elements-in-two-binary-search-trees",
#           "link": "https://leetcode.cn/problems/all-elements-in-two-binary-search-trees/",
#           "difficulty": "[Removed to avoid UTF-8 error]",
#           "description": "",
#           "participants": []
#         }
#       ]
#     }
#
#     # before each test, load the data and write to ddl_data.json (make sure the file is always the same)
#     def setUp(self):
#         with open("leetcode-test.json", "w", encoding='utf-8') as f:
#             json.dump(self.leetcode_data, f, indent=4, separators=(',', ': '))
#
#     # after each test, delete the ddl_data.json to keep directory clear
#     def tearDown(self):
#         if os.path.exists("leetcode-test.json"):
#             os.remove("leetcode-test.json")
#
#     def test_load(self):
#         leetcode = Leetcode("leetcode-test.json")
#         self.assertEqual(self.leetcode_data, leetcode.question_list)
#
#     def test_store(self):
#         # correct answer
#         with open("leetcode-test-temp.json", "w", encoding='utf-8') as f:
#             json.dump(self.leetcode_data, f, indent=4, separators=(',', ': '))
#         leetcode = Leetcode("leetcode-test.json")
#         leetcode.store_questions()
#
#         self.assertEqual(0, os.system("diff leetcode-test.json leetcode-test-temp.json"))
#
#         if os.path.exists("leetcode-test-temp.json"):
#             os.remove("leetcode-test-temp.json")
#
#     # skip the test when there is no chromedriver installed.
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_get_question_details(self):
#         result = Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lcof')
#         answer = {
#             'name': '剑指 Offer 03. 数组中重复的数字',
#             'id': 'shu-zu-zhong-zhong-fu-de-shu-zi-lcof',
#             'link': 'https://leetcode.cn/problems/shu-zu-zhong-zhong-fu-de-shu-zi-lcof',
#             'difficulty': '简单'
#         }
#         self.assertEqual(answer, result)
#
#         result = Leetcode.get_prob_detail_from_id('shopping-offers')
#         answer = {
#             'name': '638. 大礼包',
#             'id': 'shopping-offers',
#             'link': 'https://leetcode.cn/problems/shopping-offers',
#             'difficulty': '中等'
#         }
#         self.assertEqual(answer, result)
#
#         # extra slash at the end is also valid
#         result = Leetcode.get_prob_detail_from_id('shopping-offers/')
#         # temporarily we think the id/link should not has the extra slash
#         self.assertEqual(answer, result)
#         result = Leetcode.get_prob_detail_from_id('shopping-offers///')
#         self.assertEqual(answer, result)
#         result = Leetcode.get_prob_detail_from_id('//shopping-offers///')
#         self.assertEqual(answer, result)
#         result = Leetcode.get_prob_detail_from_id('/shopping-offers')
#         self.assertEqual(answer, result)
#
#         # non-existing id
#         self.assertEqual({}, Leetcode.get_prob_detail_from_id('shu-zu-zhong-zhong-fu-de-shu-zi-lf'))
#         self.assertEqual({}, Leetcode.get_prob_detail_from_id('shoppingoffers'))
#         self.assertEqual({}, Leetcode.get_prob_detail_from_id(''))
#         self.assertEqual({}, Leetcode.get_prob_detail_from_id('  '))
#         self.assertEqual({}, Leetcode.get_prob_detail_from_id('#$!%gb"123"haha'))
#
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_user_recent_submission(self):
#         # This is hard to test since the users' submission records can change from time to time
#         # so we just perform some sanity tests
#
#         result = Leetcode.get_recent_passed_submission('enor2017')
#         self.assertFalse(not result)            # not empty check
#         self.assertGreater(len(result), 2)      # at least 2 submissions
#
#     @unittest.skip("Change to latest data if you want to test.")
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_check_finish_problem(self):
#         # This is also hard to test, by default we skip this test,
#         # when want to test, you should modify the variables below
#         self.assertTrue(Leetcode.check_finish_problem('713. 乘积小于 K 的子数组', 'enor2017'))
#         self.assertFalse(Leetcode.check_finish_problem('1. 两数之和', 'enor2017'))
#
#         # test invalid problem name
#         self.assertFalse(Leetcode.check_finish_problem('haha testing', 'enor2017'))
#
#     def test_query_invalid_command(self):
#         leetcode = Leetcode("leetcode-test.json")
#
#         message_parts = ["[dummy]", "leet", "invalid_command"]
#         qq = "123456789"
#         self.assertTrue("Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = ["[dummy]", "leet", ""]
#         self.assertTrue("Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = ["[dummy]", "leet", "  "]
#         self.assertTrue("Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = ["[dummy]", "leet", "%5289nd^^\"()"]
#         self.assertTrue("Error" in leetcode.process_query(message_parts, qq))
#
#         # Below are program bugs, we should not pass non-leetcode query into this function
#         message_parts = ["[dummy]", "haha", " "]
#         self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = ["[dummy]", " "]
#         self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = ["[dummy]"]
#         self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = []
#         self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))
#
#         message_parts = None
#         # there should be a warning of passing None to List
#         self.assertTrue("Internal Error" in leetcode.process_query(message_parts, qq))
#
#     def test_query_help(self):
#         leetcode = Leetcode("leetcode-test.json")
#         message_parts = ["[dummy]", "leet", "help"]
#         qq = "12345678"
#         # check some essential keywords
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertTrue("leet help" in result_message)
#         self.assertTrue("leet submit" in result_message)
#         self.assertTrue("leet insert" in result_message)
#         self.assertTrue("leet delete" in result_message)
#         self.assertTrue("leet today" in result_message)
#         self.assertTrue("leet username" in result_message)
#         self.assertTrue("leet register" in result_message)
#         # should not contain error
#         self.assertFalse("Error" in result_message)
#
#     def test_get_questions_on_date(self):
#         # this test the function, not the query
#         leetcode = Leetcode("leetcode-test.json")
#         answer = [{'name': '978. [Removed to avoid UTF-8 error]',
#                    'id': 'longest-turbulent-subarray',
#                    'link': 'https://leetcode.cn/problems/longest-turbulent-subarray/',
#                    'difficulty': '[Removed to avoid UTF-8 error]', 'description': 'dp', 'participants': ['enor2017']},
#                   {'name': '1305. [Removed to avoid UTF-8 error]',
#                    'id': 'all-elements-in-two-binary-search-trees',
#                    'link': 'https://leetcode.cn/problems/all-elements-in-two-binary-search-trees/',
#                    'difficulty': '[Removed to avoid UTF-8 error]', 'description': '', 'participants': []}]
#         # get the questions for today
#         self.assertEqual(answer, leetcode.get_question_on_date())
#         self.assertEqual(answer, leetcode.get_question_on_date(str(datetime.date.today())))
#
#         # get the questions for a day without questions
#         self.assertEqual([], leetcode.get_question_on_date('2000-01-01'))
#
#     def test_query_get_questions_on_date(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#
#         answer = """[TBA]题目列表:
# ==========
# 题目名称: 978. [Removed to avoid UTF-8 error]
# 题目链接: https://leetcode.cn/problems/longest-turbulent-subarray/
# 题目难度: [Removed to avoid UTF-8 error]
# 已完成名单: ['enor2017']
# ==========
# 题目名称: 1305. [Removed to avoid UTF-8 error]
# 题目链接: https://leetcode.cn/problems/all-elements-in-two-binary-search-trees/
# 题目难度: [Removed to avoid UTF-8 error]
# 已完成名单: []
# """
#         self.assertEqual(answer.replace('[TBA]', '今日'),
#                          leetcode.process_query(['dummy', 'leet', 'today'], qq))
#
#         self.assertEqual('[Error] 日期2000-01-01还没有题目哦.',
#                          leetcode.process_query(['dummy', 'leet', '2000-01-01'], qq))
#         # this will not be passed into date query
#         self.assertEqual('[Error] Invalid syntax. Use "leet help" to check usage.',
#                          leetcode.process_query(['dummy', 'leet', '84-2'], qq))
#         self.assertEqual(answer.replace('[TBA]', str(datetime.date.today()) + '的'),
#                          leetcode.process_query(['dummy', 'leet', str(datetime.date.today())], qq))
#
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_query_insert_questions(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#         answer = """[TBA]题目列表:
# ==========
# 题目名称: 638. 大礼包
# 题目链接: https://leetcode.cn/problems/shopping-offers
# 题目难度: 中等
# 已完成名单: []
# """
#         message_parts = ["[dummy]", "leet", "insert", "2000-01-01", "shopping-offers"]
#         leetcode.process_query(message_parts, qq)
#         self.assertEqual(answer.replace('[TBA]', "2000-01-01" + '的'),
#                          leetcode.process_query(['dummy', 'leet', "2000-01-01"], qq))
#
#     def test_query_insert_questions_invalid_format(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#
#         error_message = '[Error] 请使用leet insert <date> <question id> <tags> 插入题目, 其中<date>格式为YYYY-MM-DD, ' \
#                         '多个tag用空格分隔, 没有tag请留空.'
#         message_parts_collections = [["[dummy]", "leet", "insert"],                             # invalid length
#                                      ["[dummy]", "leet", "insert", ""],                         # invalid length
#                                      ["[dummy]", "leet", "insert", "2000-01-01"],               # invalid length
#                                      ["[dummy]", "leet", "insert", "help"],                     # help message
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(error_message, result_message)
#
#         date_error = '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
#         message_parts_collections = [["[dummy]", "leet", "insert", "02-01-2000", "dummy_id"],   # invalid date
#                                      ["[dummy]", "leet", "insert", "", "dummy_id"],             # invalid date
#                                      ["[dummy]", "leet", "insert", "$@98an1", "dummy_id"]       # invalid date
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(date_error, result_message)
#
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_query_insert_questions_invalid_id(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#         error_message = '[Error] 找不到id为"{}"的题目. 如果你认为这是一个错误，请联系管理员.'
#
#         message_parts = ["[dummy]", "leet", "insert", "2000-01-01", "haha_id"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(error_message.format("haha_id"), result_message)
#
#         message_parts = ["[dummy]", "leet", "insert", "2000-01-01", ""]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(error_message.format(""), result_message)
#
#         message_parts = ["[dummy]", "leet", "insert", "2000-01-01", " "]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(error_message.format(" "), result_message)
#
#         message_parts = ["[dummy]", "leet", "insert", "2000-01-01", "/"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(error_message.format("/"), result_message)
#
#     def test_query_delete_questions(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#         today_str = str(datetime.date.today())
#
#         # delete the question
#         message_parts = ["[dummy]", "leet", "delete", today_str, "longest-turbulent-subarray"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f"成功删除题目: longest-turbulent-subarray, 日期为: {today_str}", result_message)
#         expected = """今日题目列表:
# ==========
# 题目名称: 1305. [Removed to avoid UTF-8 error]
# 题目链接: https://leetcode.cn/problems/all-elements-in-two-binary-search-trees/
# 题目难度: [Removed to avoid UTF-8 error]
# 已完成名单: []
# """
#         display_query = ["[dummy]", "leet", "today"]
#         # each time use a new instance to check if file is stored correctly
#         leetcode = Leetcode("leetcode-test.json")
#         self.assertEqual(expected, leetcode.process_query(display_query, qq))
#
#         # try to delete second time
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f'[Error] 日期为"{today_str}"的题目中没有id为"longest-turbulent-subarray"的题目.',
#                          result_message)
#         self.assertEqual(expected, leetcode.process_query(display_query, qq))
#
#         # delete the second question
#         message_parts = ["[dummy]", "leet", "delete", today_str, "all-elements-in-two-binary-search-trees"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f"成功删除题目: all-elements-in-two-binary-search-trees, 日期为: {today_str}", result_message)
#         expected = "[Error] 今天还没有题目哦."
#         leetcode = Leetcode("leetcode-test.json")
#         self.assertEqual(expected, leetcode.process_query(display_query, qq))
#
#         # try to delete second time
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f'[Error] 日期为"{today_str}"的题目中没有id为"all-elements-in-two-binary-search-trees"的题目.',
#                          result_message)
#         self.assertEqual(expected, leetcode.process_query(display_query, qq))
#
#     def test_query_delete_questions_invalid(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#
#         error_message = '[Error] 请使用leet delete <date> <question id> 删除题目, 其中<date>格式为YYYY-MM-DD'
#         message_parts_collections = [["[dummy]", "leet", "delete"],                             # invalid length
#                                      ["[dummy]", "leet", "delete", "2000-01-01"],               # invalid length
#                                      # invalid length
#                                      ["[dummy]", "leet", "delete", "2000-01-01", "balabala", "balabala"],
#                                      ["[dummy]", "leet", "delete", "help"],                     # help message
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(error_message, result_message)
#
#         date_error = '[Error] 日期格式不合法, 请输入YYYY-MM-DD格式的日期.'
#         message_parts_collections = [["[dummy]", "leet", "delete", "02-01-2000", "dummy_id"],   # invalid date
#                                      ["[dummy]", "leet", "delete", "", "dummy_id"],             # invalid date
#                                      ["[dummy]", "leet", "delete", "$@98an1", "dummy_id"]       # invalid date
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(date_error, result_message)
#
#         # certain date doesn't contain that question
#         today_str = str(datetime.date.today())
#         message_parts = ["[dummy]", "leet", "delete", today_str, "lalala"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f'[Error] 日期为"{today_str}"的题目中没有id为"lalala"的题目.',
#                          result_message)
#         # check the display result
#         expected = """今日题目列表:
# ==========
# 题目名称: 978. [Removed to avoid UTF-8 error]
# 题目链接: https://leetcode.cn/problems/longest-turbulent-subarray/
# 题目难度: [Removed to avoid UTF-8 error]
# 已完成名单: ['enor2017']
# ==========
# 题目名称: 1305. [Removed to avoid UTF-8 error]
# 题目链接: https://leetcode.cn/problems/all-elements-in-two-binary-search-trees/
# 题目难度: [Removed to avoid UTF-8 error]
# 已完成名单: []
# """
#         display_query = ["[dummy]", "leet", "today"]
#         leetcode = Leetcode("leetcode-test.json")   # use a new instance
#         self.assertEqual(expected, leetcode.process_query(display_query, qq))
#
#         # certain date has no question
#         message_parts = ["[dummy]", "leet", "delete", "1999-01-01", "longest-turbulent-subarray"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual('[Error] 日期为"1999-01-01"的题目中没有id为"longest-turbulent-subarray"的题目.',
#                          result_message)
#
#     @unittest.skip("Change to latest data if you want to test. "
#                    "Make sure your account provided passed 'shopping-offers', but not"
#                    "'two-sum' to ensure correctness")
#     @unittest.skipUnless(check_exists_chrome_driver(), "No chrome driver installed.")
#     def test_query_submit(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "2220038250"  # change to your qq account, and make sure it's in user.json
#         today_str = str(datetime.date.today())
#
#         # invalid: using problem id instead of name
#         message_parts = ["[dummy]", "leet", "submit", "longest-turbulent-sub"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual("[Error] 今天没有名为'longest-turbulent-sub'的题目哦!", result_message)
#
#         # insert new problems and submit
#         # this is because only in this way can we retrieve a valid problem name
#         # otherwise we removed it to avoid UTF8 error
#         insert_1 = ["[dummy]", "leet", "insert", today_str, "shopping-offers"]
#         leetcode.process_query(insert_1, qq)
#         insert_2 = ["[dummy]", "leet", "insert", today_str, "two-sum"]
#         leetcode.process_query(insert_2, qq)
#         get_list = ["[dummy]", "leet", "today"]
#         current_prob_list = leetcode.process_query(get_list, qq)
#         self.assertIn("shopping-offers", current_prob_list,
#                       "[Test Internal Error] Assumption not satisfied, 'shopping-offers' not inserted.")
#         self.assertIn("two-sum", current_prob_list,
#                       "[Test Internal Error] Assumption not satisfied, 'two-sum' not inserted.")
#
#         # submit single question
#         q_name = "638. 大礼包"
#         message_parts = ["[dummy]", "leet", "submit", q_name]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f"提交题目 {q_name} 成功!", result_message)
#         # check already finished    TODO: this oracle is not strong enough, modify later
#         self.assertIn('enor2017', leetcode.process_query(['dummy', 'leet', 'today'], qq))
#
#         # submit unfinished single question
#         q_name = "1. 两数之和"
#         message_parts = ["[dummy]", "leet", "submit", q_name]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(f"您好像还没有完成题目 {q_name} 哦.", result_message)
#
#         # submit all
#         message_parts = ["[dummy]", "leet", "submit"]
#         result_message = leetcode.process_query(message_parts, qq)
#         # TODO: below oracles are not strong enough, try to use regex instead
#         self.assertIn("您已成功提交!", result_message)
#         self.assertIn("638. 大礼包", result_message)
#         self.assertIn("您好像还没有完成这道题.", result_message)
#         self.assertIn("1. 两数之和", result_message)
#
#     def test_query_submit_invalid(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#
#         # invalid query syntax
#         message_parts = ["[dummy]", "leet", "submit", "invalid field", "invalid field 2"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual("[Error] Invalid syntax. Use \"leet help\" to check usage.", result_message)
#
#         # user not registered
#         message_parts = ["[dummy]", "leet", "submit", "longest-turbulent-subarray"]
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual("我还不知道您的LeetCode账户名哦，试试leet register <your leetcode username>",
#                          result_message)
#
#     # === User operations ===
#     # We cannot specify where to load data under current implementation, so we just modify original file.
#     # Remember to modify back after testing. Do not mess it up!
#     def test_register_invalid(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "12345678"
#         error_message = '[Error]正确食用方法: leet register <your leetcode username>'
#
#         message_parts_collections = [["[dummy]", "leet", "register"],                   # invalid length
#                                      ["[dummy]", "leet", "register", "test", "extra"],  # invalid length
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(error_message, result_message)
#
#     # 'register' is also tested here
#     def test_get_username(self):
#         leetcode = Leetcode("leetcode-test.json")
#         message_parts = ["[dummy]", "leet", "username"]
#         message_parts_reg = ["[dummy]", "leet", "register", "testing-leetcode-username"]
#         err_msg_unknown_user = '我还不知道您的LeetCode用户名诶，要不要试试 leet register <your leetcode username>'
#
#         qq = "777788889999"  # a valid username (registered)
#         result_message_from_user_op = leetcode.process_query(message_parts_reg, qq)
#         self.assertTrue('Successfully' in result_message_from_user_op)  # check if register functions well
#
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual('您已绑定LeetCode的用户名是: testing-leetcode-username', result_message)
#
#         # this part checks register, for an already registered user to update username
#         message_parts_reg_upd = ["[dummy]", "leet", "register", "testing-new-username"]
#         result_message = leetcode.process_query(message_parts_reg_upd, qq)
#         self.assertTrue('Successfully update' in result_message)
#         # check updated username
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual('您已绑定LeetCode的用户名是: testing-new-username', result_message)
#
#         # remove the inserted data in user.json to keep database clean
#         user_op = UserOperation.UserOperation()
#         user_op.delete_user(qq)
#
#         qq = "1234567887654321"  # ensure an invalid qq account
#         result_message = leetcode.process_query(message_parts, qq)
#         self.assertEqual(err_msg_unknown_user, result_message)
#
#     def test_get_username_invalid(self):
#         leetcode = Leetcode("leetcode-test.json")
#         qq = "1234567887654321"     # ensure an invalid qq account
#         err_msg_invalid_query = '[Error]正确食用方法: leet username'
#
#         message_parts_collections = [["[dummy]", "leet", "username", ""],           # invalid length
#                                      ["[dummy]", "leet", "username", "testing"],    # invalid length
#                                      ]
#         for message_parts in message_parts_collections:
#             result_message = leetcode.process_query(message_parts, qq)
#             self.assertEqual(err_msg_invalid_query, result_message)
#
#
# if __name__ == '__main__':
#     unittest.main()
