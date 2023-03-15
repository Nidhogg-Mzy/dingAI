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

Receive = None
def arg_parser():
    parser = argparse.ArgumentParser(description="bot_parser")
    parser.add_argument("--app", type=str, default='dingtalk', help="app you want to deploy your bot on")
    parser.add_argument('--debug', action='store_true', help='Add this flag if in debug mode,'
                                                             'the program will use testing accounts')
    args = parser.parse_args()
    global Receive
    Receive = __import__(f'{args.app}_receive')

class app:
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
                Receive.send_msg({'msg_type': 'group', 'number': '705716007', 'msg':
                    f'大家早上好呀, 又是新的一天，来看看今天还有哪些ddl呢>_<\n{ddl_service.process_query("ddl today".split(" "), "0")}'})
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
                Receive.send_msg({'msg_type': 'group_notice', 'number': Receive.GROUP_ACCOUNT,
                                  'msg': Leetcode.display_questions(Leetcode.question_list)})
                time.sleep(60 * 60 * 23 + 60 * 30)  # sleep 23h 30min
            time.sleep(20)  # allow some buffer time.


    @staticmethod
    def get_answer(text):
        # get reply for bot api
        data = Receive.get_data(text)
        url = 'https://api.ownthink.com/bot'  # API接口
        response = requests.post(url=url, data=data)
        response.encoding = 'utf-8'
        result = response.json()
        try:
            answer = result['data']['info']['text']
        except TypeError:
            return "抱歉，我没有理解您的意思，请换一个问题试试？"
        return answer


    @staticmethod
    def rev_private_msg(rev):
        if rev['raw_message'] == '在吗':
            qq = rev['sender']['user_id']
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)]})
        elif rev['raw_message'] == '你在哪':
            qq = rev['sender']['user_id']
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': '我无处不在'})
        # TODO: check if there will be index-out-of-bound issue
        elif rev['raw_message'].split(' ')[0] == '歌词':
            qq = rev['sender']['user_id']
            if len(rev['raw_message'].split(' ')) < 2:
                Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': '请输入：歌曲<空格><歌曲名>来获得歌曲链接哦'})
            else:
                song = rev['raw_message'].replace('歌词', '')
                d = Search()
                music_id = d.search_song(song)
                if music_id is None:
                    Receive.send_msg(
                        {'msg_type': 'private', 'number': qq, 'msg': '呜呜呜人家找不到嘛，换首歌试试吧'})
                else:
                    text = Search.get_lyrics(music_id)
                    Receive.send_msg(
                        {'msg_type': 'private', 'number': qq, 'msg': text})
        elif rev['raw_message'].split(' ')[0] == '歌曲':
            qq = rev['sender']['user_id']
            if len(rev['raw_message'].split(' ')) < 2:
                Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': '请输入：歌曲<空格><歌曲名>来获得歌曲链接哦'})
            else:
                song = rev['raw_message'].replace('歌曲', '')
                d = Search()
                music_id = d.search_song(song)
                if music_id is None:
                    Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': '呜呜呜人家找不到嘛，换首歌试试吧'})
                else:
                    Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': f'[CQ:music,type=163,id={music_id}]'})
        else:
            qq = rev['sender']['user_id']
            content = rev['raw_message']
            if content == '':
                answer = '根本搞不懂你在讲咩话，说点别的听听啦'
            else:
                answer = app.get_answer(content)
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': answer})



    @staticmethod
    def rev_group_msg(rev):
        group = rev['group_id']
        if f'[CQ:at,qq={Receive.BOT_ACCOUNT}]' in rev["raw_message"]:
            qq = rev['sender']['user_id']
            message_parts = rev['raw_message'].strip().split(' ')
            if len(message_parts) < 2:
                Receive.send_msg({'msg_type': 'group', 'number': group, 'msg': '蛤?'})
                return
            if message_parts[1] == '在吗':
                Receive.send_msg(
                    {'msg_type': 'group', 'number': group,
                     'msg': Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)]})
            elif message_parts[1] in ['wait', 'waitlist', 'Wait']:
                Receive.send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f"[CQ:at,qq={qq}]\n" + app.get_waitlist(str(qq))})
            # leetcode feature
            elif message_parts[1] == 'leet':
                Receive.send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f"[CQ:at,qq={qq}]\n" + Leetcode.process_query(message_parts, qq)})
            # DDL feature
            elif message_parts[1] == 'ddl':
                Receive.send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f"[CQ:at,qq={qq}]\n" + DDLService.process_query(message_parts[1:], qq)})
            # TODO: add help reply
            else:
                content = ""
                for i in range(1, len(message_parts)):
                    content += message_parts[i] + " "
                Receive.send_msg({'msg_type': 'group', 'number': group,
                                  'msg': f'[CQ:at,qq={qq}]' + Receive.get_answer(content)})


    @staticmethod
    def message_process_tasks():
        """
        All private/group message processing are done here.
        """
        while True:
            received = Receive.rev_msg()
            try:
                if received["post_type"] == "message":
                    # private message
                    if received["message_type"] == "private":
                        Receive.rev_private_msg(received)
                    # group message
                    elif received["message_type"] == "group":
                        Receive.rev_group_msg(received)
            # TODO: consider enlarge type of Error?
            except TypeError as e:
                # This error will be reported to developers via qq private message.
                error_msg = '[Internal Error] TypeError while trying to reply message. ' \
                            'If the message received is too long, try to' + \
                            'release the length restriction. (currently 4096)\n' + \
                            f'[Exception Message] {e}\n ' \
                            f'Message received: {received}'
                # TODO: specify admin account in config file
                Receive.send_msg({'msg_type': 'private', 'number': '2220038250', 'msg': error_msg})
                Receive.send_msg({'msg_type': 'private', 'number': '3429582673', 'msg': error_msg})
                # also record in log
                print(f'##### Error\n{error_msg}')

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