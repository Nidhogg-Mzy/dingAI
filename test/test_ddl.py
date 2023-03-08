## temporarily disable the test, as it is database-free version
# import json
# import os
# import unittest
# from unittest.mock import patch
# from DDLService import DDLService
#
# # decorator to replace the constructor
# def mock_init_decorator(func):
#     # rewrite the constructor, load ddl data from ddl_data.json
#     def mock_init(self):
#         self.filename = "ddl_data.json"
#         self.ddl_list = []
#         self.load_ddl_from_file()
#
#     def wrapper(*args, **kwargs):
#         with patch.object(DDLService, '__init__', mock_init):
#             return func(*args, **kwargs)
#
#     return wrapper
#
#
# class DDLTest(unittest.TestCase):
#     # before each test, load the data and write to ddl_data.json (make sure the file is always the same)
#     def setUp(self):
#         self.original_ddl_list = [
#                 {
#                     "title": "COMP2012 PA2",
#                     "date": "8888-04-02",
#                     "participants": ["2220038250", "12345678"],
#                     "description": "Due at 23:59 PM."
#                 },
#                 {
#                     "title": "COMP2211 Midterm Exam",
#                     "date": "2000-04-02",
#                     "participants": ["2220038250", "3429582673"],
#                     "description": "2PM - 4PM. Join at 1PM for attendance checking."
#                 }
#             ]
#
#         with open("ddl_data.json", "w") as f:
#             json.dump(self.original_ddl_list, f, indent=4, separators=(',', ': '))
#
#     # after each test, delete the ddl_data.json to keep directory clear
#     def tearDown(self):
#         if os.path.exists("ddl_data.json"):
#             os.remove("ddl_data.json")
#
#     @mock_init_decorator
#     def test_load_ddl_from_file(self):
#         ddl_service = DDLService()
#         self.assertEqual(self.original_ddl_list, ddl_service.ddl_list)
#
#     @mock_init_decorator
#     def test_remove_expired_ddl(self):
#         ddl_service = DDLService()
#         ddl_service.remove_expired_ddl()
#
#         # check correctly removed
#         self.assertEqual([self.original_ddl_list[0]], ddl_service.ddl_list)
#
#         # check correctly stored
#         ddl_service_new = DDLService()
#         self.assertEqual([self.original_ddl_list[0]], ddl_service_new.ddl_list)
#
#
# if __name__ == '__main__':
#     unittest.main()
