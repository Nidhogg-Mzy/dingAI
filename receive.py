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

class Receive:
    ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ListenSocket.bind(('127.0.0.1', 5701))
    ListenSocket.listen(100)
    filename = 'config.json'

    # const variable should be UPPER_CASE style
    BOT_ACCOUNT, GROUP_ACCOUNT = 0, 0

    @staticmethod
    def send_msg(resp_dict):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ip = '127.0.0.1'
        client.connect((ip, 5700))

        msg_type = resp_dict['msg_type']  # message type: group or private
        number = resp_dict['number']  # reply to whom (person id or group id)
        msg = resp_dict['msg']  # message to reply

        # encode special characters
        msg = msg.replace(" ", "%20")
        msg = msg.replace("\n", "%0a")

        api_endpoints = {'group': 'GET /send_group_msg?group_id=',
                         'private': 'GET /send_private_msg?user_id=',
                         'group_notice': 'POST /_send_group_notice?group_id='}
        if msg_type in api_endpoints.keys():
            payload = f'{api_endpoints[msg_type]}{number}&message=' \
                      f'{msg} HTTP/1.1\r\nHost:{ip}:5700\r\nConnection: close\r\n\r\n'
        else:
            payload = ''
        print("Send: " + payload)
        client.send(payload.encode("utf-8"))
        client.close()
        return 0

    @staticmethod
    def read_account_info(debug: bool):
        with open(Receive.filename, "r", encoding='utf-8') as f:
            accounts = json.load(f)["accounts"]
            # use testing account and group if debug is True
            Receive.BOT_ACCOUNT = accounts['testing_bot'] if debug else accounts['official_bot']
            Receive.GROUP_ACCOUNT = accounts['testing_group'] if debug else accounts['testing_bot']

    @staticmethod
    def request_to_json(msg):
        for i in range(len(msg)):
            if msg[i] == "{" and msg[-1] == "\n":
                return json.loads(msg[i:])
        return None

    @staticmethod
    def rev_msg():  # json or None
        client, address = Receive.ListenSocket.accept()
        request = client.recv(4096).decode('utf-8', 'ignore')
        rev_json = Receive.request_to_json(request)
        http_response_header = '''HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n\r\n
        '''
        client.sendall(http_response_header.encode(encoding='utf-8'))
        client.close()
        return rev_json

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

    # reply messages for private/group
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']

    @staticmethod
    def rev_private_msg(rev):
        if rev['raw_message'] == '在吗':
            qq = rev['sender']['user_id']
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)]})
        elif rev['raw_message'] == '你在哪':
            qq = rev['sender']['user_id']
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': '我无处不在'})
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
                answer = Receive.get_answer(content)
            Receive.send_msg({'msg_type': 'private', 'number': qq, 'msg': answer})

    @staticmethod
    def rev_group_msg(rev):
        group = rev['group_id']
        if f'[CQ:at,qq={Receive.BOT_ACCOUNT}]' in rev["raw_message"]:
            qq = rev['sender']['user_id']
            message_parts = rev['raw_message'].strip().split(' ')
            if message_parts[1] == '在吗':
                Receive.send_msg(
                    {'msg_type': 'group', 'number': group,
                     'msg': Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)]})
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Add this flag if in debug mode,'
                                                             'the program will use testing accounts')
    args = parser.parse_args()

    # initiate all the accounts
    Receive.read_account_info(debug=args.debug)
    # add a thread to check scheduled tasks
    DataBase.init_database()
    print("database initialized")
    trd_scheduled = Thread(target=Receive.check_scheduled_task)
    trd_scheduled.start()

    # add a thread to process message reply tasks
    trd_msg_reply = Thread(target=Receive.message_process_tasks)
    trd_msg_reply.start()

    # add a thread to update the question list and send a group notice every midnight
    trd_daily_update = Thread(target=Receive.daily_update)
    trd_daily_update.start()


