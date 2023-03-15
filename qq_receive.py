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
    def get_data(text):
        # info to request api
        # TODO: specify this in config file
        data = {
            "appid": "a612dbe7965b53eeb5eaf26edccc8c94",
            "userid": "sKJAeMs3",
            "spoken": text,
        }
        return data



    # reply messages for private/group
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']





# TODO: make all about hkust into a new module.
# TODO: I, personally, don't want this to be released to public.



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

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


