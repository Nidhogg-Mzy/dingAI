import base64
import hashlib
import hmac
import json
import random
import configparser
import requests
from flask import Flask, jsonify, make_response, request
from services import SERVICES_MAP
from services.medium_daily_push import MediumService
import threading


class Receive:
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']
    app = Flask(__name__)
    configs = configparser.ConfigParser()
    configs.read('config.ini')

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
        @return a bool if the sign is a valid sign
        """
        timestamp = header['timestamp']
        app_secret = 'this is a secret'
        app_secret_enc = app_secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{app_secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign == header['sign']

    @staticmethod
    def parse_msg(msgtype: str, msg: str, user_id: str, is_at_all: bool = False):
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
                "text": {
                    "content": msg
                },
                "msgtype": msgtype,
                "at": {
                    "atUserIds": [
                        user_id
                    ],
                    "isAtAll": is_at_all
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
                        user_id
                    ],
                    "isAtAll": is_at_all
                }
            }
        return data

    @staticmethod
    def send_feedcard_msg(titles: list, message_urls: list, image_urls: list):
        result = []
        headers = {'Content-Type': 'application/json'}
        for title, message_url, image_url in zip(titles, message_urls, image_urls):
            item = {
                "title": title,
                "messageURL": message_url,
                "picURL": image_url
            }
            result.append(item)

        # Convert the list of dictionaries to a JSON array
        links = json.dumps(result)
        data = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": links
            }
        }
        url = Receive.configs['dingtalk']['url']
        print(requests.post(url, json=data, headers=headers, timeout=30).text)

    @staticmethod
    def rev_msg():  # json or None
        body = json.loads(request.data.decode('utf-8'))
        parsed_msg = Receive.parse_body(body)
        return parsed_msg

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
        return Receive.handle_reply(received)

    @staticmethod
    def handle_reply(received):
        user_id = received['senderId']
        message_parts = received['msg'].strip().split(' ')
        if len(message_parts) < 1:
            return_msg = Receive.parse_msg(msgtype='markdown', user_id=user_id, msg='蛤?')
        elif message_parts[0] == '在吗':
            return_msg = Receive.parse_msg(msgtype='markdown', user_id=user_id,
                                           msg=Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)])
        else:
            try:
                service = SERVICES_MAP[message_parts[0]]
            except KeyError:
                return_msg = Receive.parse_msg(msgtype='markdown', user_id=user_id,
                                               msg="We currently do not support this kind of service")
            else:
                service.load_config(Receive.configs)
                return_msg = Receive.parse_msg(msgtype='markdown', user_id=user_id,
                                               msg=service.process_query(message_parts, user_id))
        response = make_response(jsonify(return_msg))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    medium_thread = threading.Thread(target=lambda: (
        MediumService.init_service(Receive.send_feedcard_msg, Receive.configs),
        print('medium service initialized'),
        MediumService.start_scheduler()
    ))
    receive_thread = threading.Thread(target=lambda: Receive.app.run('0.0.0.0', 60001))
    medium_thread.start()
    receive_thread.start()
    medium_thread.join()
    receive_thread.join()
