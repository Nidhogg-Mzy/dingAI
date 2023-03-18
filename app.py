import json
import random
import socket
import time
import datetime
import argparse
from threading import Thread
import requests
from Leetcode import Leetcode
from DDLService import DDLService
from multi_func_reply import Search
from database import DataBase

device = None


class App:
    @staticmethod
    def check_scheduled_task():
        """
        This function stores scheduled tasks.
        TODO: re-write this using some scheduler package
        """
        while True:
            # get current time in UTC+8
            curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            # 8:00 AM, show ddl today
            if curr_time.hour == 8 and curr_time.minute == 0:
                ddl_service = DDLService()
                if device == 'qq':
                    Receive.send_msg({'msg_type': 'group_notice', 'number': Receive.GROUP_ACCOUNT,
                                      'msg': Leetcode.display_questions(Leetcode.question_list)})
                else:
                    # TODO: add send message in dingtalk format
                    pass
                ddl_service.remove_expired_ddl()  # remove expired ddl timely
                time.sleep(60)

            time.sleep(20)  # allow some buffer time.

    @staticmethod
    def daily_update():
        """
        Update the question_list in leetcode
        Send a group notice at midnight contains the message of today's question
        TODO: re-write this using some scheduler package
        """
        while True:
            # get current time in UTC+8
            curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            # check if it is midnight
            if curr_time.hour == 0 and curr_time.minute == 0:
                Leetcode.question_list = DataBase.get_question_on_date(curr_time.strftime('%Y-%m-%d'))
                if device == 'qq':
                    Receive.send_msg({'msg_type': 'group_notice', 'number': Receive.GROUP_ACCOUNT,
                                      'msg': Leetcode.display_questions(Leetcode.question_list)})
                else:
                    # TODO: add send message in dingtalk format
                    pass
                time.sleep(60 * 60 * 23 + 60 * 30)  # sleep 23h 30min
            time.sleep(20)  # allow some buffer time.

    @staticmethod
    def get_data(text):
        # info to request api
        # TODO: specify this in config file
        data = {
            "appid": "a612dbe7965b53eeb5eaf26edccc8c94",
            "userid": "sKJAeMs3",
            "spoken": text,
        }
        return data

    @staticmethod
    def get_answer(text):
        # get reply for bot api
        data = App.get_data(text)
        url = 'https://api.ownthink.com/bot'  # API接口
        response = requests.post(url=url, data=data)
        response.encoding = 'utf-8'
        result = response.json()
        try:
            answer = result['data']['info']['text']
        except TypeError:
            return "抱歉，我没有理解您的意思，请换一个问题试试？"
        return answer

    def get_waitlist(qq: str) -> str:
        url = "https://w5.ab.ust.hk/msapi/sis/stdt_class_enrl/%7BstdtID%7D"
        payload = {}

        def get_header(qq: str) -> dict:
            with open("test.config", "r") as f:
                all_configs = json.load(f)["hkust_oauth_token"]
            return {
                'Authorization': f'Bearer {all_configs[qq]}',
                'Cookie': 'language=en-US'
            }

        headers = get_header(qq)
        print(headers)

        response = requests.request("GET", url, headers=headers, data=payload)

        json_response = json.loads(response.text)
        stdInfo = json_response['stdtInfo'][0]
        waitList = stdInfo['studentClassWaitlist']
        info = ''
        for c in waitList:
            info += f'course code: {c["crseCode"]}, waitlist position: {c["waitPosition"]}\n'

        return info


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="bot_parser")
    parser.add_argument("--app", type=str, default='dingtalk', help="app you want to deploy your bot on")
    parser.add_argument('--debug', action='store_true', help='Add this flag if in debug mode,'
                                                             'the program will use testing accounts')
    args = parser.parse_args()
    device = args.app
    if args.app == 'qq':
        from qq_receive import Receive
    else:
        from dingtalk_receive import Receive
