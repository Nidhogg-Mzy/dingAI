import base64
import hashlib
import hmac
import json
import random
from flask import Flask, jsonify, make_response, request
from services import SERVICES_MAP
from services.gpt import GPTService


class Receive:
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']
    app = Flask(__name__)
    filename = 'config.ini'
    """

    """

    @staticmethod
    def verify_sign(header: dict) -> bool:
        """
        This function takes out the timestamp and verify the sign of the sender
            structure of header:
        {
          "Content-Type": "application/json; charset=utf-8",
          "timestamp": "1577262236757",
          "sign":"xxxxxxxxxx"
        }
        @param header: the header of the received message
        @return a bool if the sign is a validate sign
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
    def parse_msg(msgtype: str, msg: str, userId: str, isAtAll=False):
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
        headers = {'Content-Type': 'application/json'}
        if msgtype == 'text':
            data = {
                "text": {
                    "content": msg
                },
                "msgtype": msgtype,
                "at": {
                    "atUserIds": [
                        userId
                    ],
                    "isAtAll": isAtAll
                }
            }
        elif msgtype == 'markdown':
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "回复消息",
                    "text": msg
                },
                "at": {
                    "atUserIds": [
                        userId
                    ],
                    "isAtAll": isAtAll
                }
            }
        return data
        # url = 'https://oapi.dingtalk.com/robot/send?access_token=6e3b6e9db9f5b1d029615e4ea6fff2b716d77cf89a8adc9449603501bfdf9e0a'
        # print(requests.post(url, json=data, headers=headers).text)

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
                      'msg': body['text']['content'], 'senderId': body['senderStaffId'],
                      'sender_nick': body['senderNick']}
        return parsed_msg

    @staticmethod
    @app.route('/', methods=['POST', 'GET'])
    def message_process_tasks():
        """
        All private/group message processing are done here.
        """
        received = Receive.rev_msg()
        if received["conversation_type"] == "group":
            return Receive.rev_group_msg(received)

    @staticmethod
    def rev_group_msg(received):
        userId = received['senderId']
        message_parts = received['msg'].strip().split(' ')
        if len(message_parts) < 1:
            return_msg = Receive.parse_msg(msgtype='markdown', userId=userId, msg='蛤?')
        elif message_parts[0] == '在吗':
            return_msg = Receive.parse_msg(msgtype='markdown', userId=userId,
                                           msg=Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)])
        else:
            try:
                service = SERVICES_MAP[message_parts[0]]
                return_msg = Receive.parse_msg(msgtype='markdown', userId=userId,
                                               msg=service.process_query(message_parts, {'user_id': userId}))
            except KeyError:
                return_msg = "We currently do not support this kind of service"
        response = make_response(jsonify(return_msg))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    Receive.app.run('0.0.0.0', 60001)
