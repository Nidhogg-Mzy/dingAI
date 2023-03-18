import json
import socket
import requests
from flask import Flask, request


class Receive:
    ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ListenSocket.bind(('127.0.0.1', 5701))
    ListenSocket.listen(100)
    filename = 'config.json'

    # const variable should be UPPER_CASE style
    BOT_ACCOUNT, GROUP_ACCOUNT = 0, 0

    @staticmethod
    def send_msg(resp_dict):
        """
        format of text message sent
        {
            "at": {
                "atMobiles":[
                    "180xxxxxx"
                ],
                "atUserIds":[
                    "user123"
                ],
                "isAtAll": false
            },
            "text": {
                "content":"我就是我, @XXX 是不一样的烟火"
            },
            "msgtype":"text"
        }
        """
        msgtype = resp_dict['msg_type']
        data = {}
        if msgtype == 'text':
            number = resp_dict['at']['atUserIds']
            content = resp_dict['text']
            data = {
                'at': {
                    'atUserIds': [number]
                },
                'text': {
                    'content': content
                },
                'msgtype': msgtype
            }

        url = 'https://oapi.dingtalk.com/robot/send?access_token=6e3b6e9db9f5b1d029615e4ea6fff2b716d77cf89a8adc9449603501bfdf9e0a'
        requests.post(url, data=data)

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

    app = Flask(__name__)

    @staticmethod
    @app.route('/', methods=['POST'])
    def rev_msg():  # json or None
        request_body = json.loads(request.data)
        request_header = request.headers
        timestamp = request_header['timestamp']
        sign = request_header['header']
        content = request_body['text']['content']
        account = request_body['senderStaffId']
        return ''


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
