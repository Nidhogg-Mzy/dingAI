import base64
import hashlib
import hmac
import json
import random

import requests
from flask import Flask, request


class Receive:
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']
    app = Flask(__name__)
    # ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ListenSocket.bind(('127.0.0.1', 5701))
    # ListenSocket.listen(100)
    filename = 'config.ini'
    """
    structure of header:
    {
      "Content-Type": "application/json; charset=utf-8",
      "timestamp": "1577262236757",
      "sign":"xxxxxxxxxx"
    }
    """

    @staticmethod
    def verify_sign(header: dict) -> bool:
        """
        This function takes out the timestamp and verify the sign of the sender
        """
        timestamp = header['timestamp']
        app_secret = 'this is a secret'
        app_secret_enc = app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign == header['sign']

    @staticmethod
    def send_msg(msgtype: str, msg: str):
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
        data = {}
        if msgtype == 'text':
            data = {
                'text': {
                    'content': msg
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

    @staticmethod
    def rev_msg():  # json or None
        headers = dict(request.headers)
        body = json.loads(request.data.decode('utf-8'))
        parsed_msg = Receive.parse_body(body)
        return parsed_msg
        # Get the request headers
        # Return the headers and body as a JSON object

    @staticmethod
    def parse_body(body) -> dict:
        parsed_msg = {'message_type': body['msgtype'],
                      'conversation_type': 'private' if body['conversationType'] == 1 else 'group',
                      'msg': body['text']['content'], 'sender_nick': body['senderNick']}
        return parsed_msg

    @staticmethod
    @app.route('/', methods=['POST'])
    def message_process_tasks():
        """
        All private/group message processing are done here.
        """
        received = Receive.rev_msg()
        try:
            if received["conversation_type"] == "group":
                return ''
        # TODO: consider enlarge type of Error?
        except TypeError as e:
            # This error will be reported to developers via qq private message.
            error_msg = '[Internal Error] TypeError while trying to reply message. ' \
                        'If the message received is too long, try to' + \
                        'release the length restriction. (currently 4096)\n' + \
                        f'[Exception Message] {e}\n ' \
                        f'Message received: {received}'
            print(f'##### Error\n{error_msg}')

    @staticmethod
    def rev_group_msg(rev):
        message_parts = rev['msg'].strip().split(' ')
        if len(message_parts) < 2:
            Receive.send_msg(msgtype='text', msg='蛤?')
            return
        if message_parts[1] == '在吗':
            Receive.send_msg(msgtype='text', msg=Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)])
            # return Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)]
        # elif message_parts[1] in ['wait', 'waitlist', 'Wait']:
        #     Receive.send_msg(msgtype='text', msg=Receive.reply_msg[random.randint(0, len(Receive.reply_msg)
        #     Receive.send_msg({'msg_type': 'group', 'number': group,
        #                       'msg': f"[CQ:at,qq={qq}]\n" + App.get_waitlist(str(qq))})
        # # leetcode feature
        # elif message_parts[1] == 'leet':
        #     Receive.send_msg({'msg_type': 'group', 'number': group,
        #                       'msg': f"[CQ:at,qq={qq}]\n" + Leetcode.process_query(message_parts, qq)})
        # # DDL feature
        # elif message_parts[1] == 'ddl':
        #     Receive.send_msg({'msg_type': 'group', 'number': group,
        #                       'msg': f"[CQ:at,qq={qq}]\n" + DDLService.process_query(message_parts[1:], qq)})
        # # TODO: add help reply
        # else:
        #     content = ""
        #     for i in range(1, len(message_parts)):
        #         content += message_parts[i] + " "
        #     Receive.send_msg({'msg_type': 'group', 'number': group,
        #                       'msg': f'[CQ:at,qq={qq}]' + App.get_answer(content)})

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


if __name__ == '__main__':
    Receive.app.run('0.0.0.0', 1234)
