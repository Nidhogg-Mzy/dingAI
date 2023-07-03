import base64
import hashlib
import hmac
import json
import random
import logging
import configparser
import requests
from datetime import datetime, timedelta
from typing import Literal, Optional, Union
from flask import Flask, jsonify, make_response, request
from services import SERVICES_MAP
from services.medium_daily_push import MediumService


class Receive:
    reply_msg = ['在的呀小可爱', '一直在的呀', '呜呜呜找人家什么事嘛', '我无处不在', 'always here', '在的呀',
                 '在啊，你要跟我表白吗', '不要着急，小可爱正在赶来的路上，请准备好零食和饮料耐心等待哦', '有事起奏，无事退朝',
                 '你先说什么事，我再决定在不在', '搁外面躲债呢，你啥事啊直接说', '在呢，PDD帮我砍一刀呗', '爱卿，何事',
                 '只要你找我，我无时无刻不在', '我在想，你累不累，毕竟你在我心里跑一天了', '想我了，就直说嘛',
                 '我在想，用多少度的水泡你比较合适', '你看不出来吗，我在等你找我啊']
    app = Flask(__name__)
    configs = configparser.ConfigParser()
    configs.read('config.ini')

    class _AccessToken:
        """
        This class is used to get the access token of the robot.
        """
        app_key: str
        app_secret: str
        access_token: Optional[str]
        expire_time: datetime

        @classmethod    # use class method for better class variable reference
        def init_token(cls, app_key: str, app_secret: str):
            cls.app_key = app_key
            cls.app_secret = app_secret
            cls.access_token = None
            cls.expire_time = datetime.now()

        @classmethod
        def get_access_token(cls) -> str:
            """
            Returns the `x-acs-dingtalk-access-token` of robot.
            If current token is invalid, a new token will be fetched using AppKey and AppSecret.
            doc: https://open.dingtalk.com/document/orgapp/obtain-the-access_token-of-an-internal-app?spm=ding_open_doc.document.0.0.263e1563MtqouX
            
            :return: the access token of the robot
            :raises ValueError: if AppKey or AppSecret is not set, or failed to get access token
                using the given AppKey and AppSecret
            """# noqa
            if cls.app_key is None or cls.app_secret is None:
                raise ValueError('Please call init_token first.')

            if cls.access_token is None or cls.expire_time is None or cls.expire_time < datetime.now():
                url = f'https://api.dingtalk.com/v1.0/oauth2/accessToken'
                payload = {
                    'appKey': cls.app_key,
                    'appSecret': cls.app_secret
                }
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    response_json = response.json()
                    cls.access_token = response_json['accessToken']
                    cls.expire_time = datetime.now() + timedelta(seconds=int(response_json['expireIn'])) \
                                                     + timedelta(seconds=-60)   # some buffer time
                else:
                    raise ValueError(f'Failed to get access token: {response.json()}')
            return cls.access_token

    # this variable is strictly private for security reason
    __access_token = _AccessToken()
    __access_token.init_token(configs['dingtalk']['app_key'], configs['dingtalk']['app_secret'])

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
    def generate_msg_param(msg_key: Literal["sampleText", "sampleMarkdown"], msg: str) -> str:
        # TODO: user_id and at_all function?
        """
        This function generates the msg_param for sending message.

        doc: https://open.dingtalk.com/document/isvapp/bots-send-group-chat-messages
        """
        msg_param = {}
        if msg_key in ['sampleText', 'sampleMarkdown']:
            msg_param = {
                "title": "DingAI消息",
                "text": msg,
            }
        # TODO: more supported msg_key
        return str(msg_param)

    @staticmethod
    def send_msg(msg: str,
                 msg_key: Literal["sampleText", "sampleMarkdown"] = 'sampleMarkdown',
                 auth_info: dict[str, Union[str, list[str]]] = {}) -> str:
        """
        This function sends a message to the user, either in private or group chat.
        
        :param msg: the message to be sent
        :param msg_key: the type of the message, default is 'sampleMarkdown'
        :param auth_info: the auth info. For a private chat, it should be 
            {'robotCode': 'robot_code', 'userIds': ['user_id1', 'user_id2']}.
            For a group chat, it should be {'openConversationId': 'open_conversation_id'}

        doc: https://open.dingtalk.com/document/isvapp/send-single-chat-messages-in-bulk
        doc: https://open.dingtalk.com/document/isvapp/bots-send-group-chat-messages
        {
          "msgParam" : "String",
          "msgKey" : "String",
          # group chat
          "openConversationId" : "String",
          # private chat
          "robotCode" : "String",
          "userIds" : Array[String]
        }
        """# noqa
        base_url = 'https://api.dingtalk.com/v1.0/robot/{}'
        is_group_chat: bool = 'openConversationId' in auth_info
        url = base_url.format('groupMessages/send' if is_group_chat else 'oToMessages/batchSend')
        payload = {
            "msgParam": Receive.generate_msg_param(msg_key, msg),
            "msgKey": msg_key,
            **auth_info
        }
        headers = {
            'Content-Type': 'application/json',
            'x-acs-dingtalk-access-token': Receive.__access_token.get_access_token()
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    @staticmethod
    def send_feedcard_msg(titles: list, message_urls: list, image_urls: list, webhooks: list):
        """
        This function sends a feedcard message to the group chat.
        Notice that Webbook must be used in order to send feedcard-type messages.

        doc: https://open.dingtalk.com/document/orgapp/robot-message-types-and-data-format

        :param titles: a list of titles of the feedcard
        :param message_urls: a list of message urls of the feedcard
        :param image_urls: a list of image urls of the feedcard
        :param webhooks: a list of webhooks of all the groups that the message will be sent to
        """
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
        # TODO: support multiple webhooks
        url = Receive.configs['dingtalk']['url']
        print(requests.post(url, json=data, headers=headers, timeout=30).text)

    @staticmethod
    def parse_body(body) -> (dict, dict):
        parsed_msg = {
            'conversationId': body['conversationId'],
            'message_type': body['msgtype'],
            'conversation_type': 'private' if body['conversationType'] == 1 else 'group',
            'msg': body['text']['content'],
            'senderId': body['senderStaffId'],
            'sender_nick': body['senderNick']
        }
        auth_info = {}
        if parsed_msg['conversation_type'] == 'group':
            auth_info['openConversationId'] = body['conversationId']
        else:
            auth_info['robotCode'] = body['robotCode']
            auth_info['userIds'] = [parsed_msg['senderId']]
        return parsed_msg, auth_info

    @staticmethod
    @app.route('/', methods=['POST'])
    def message_process_tasks():
        """
        All private/group message processing are done here.
        """
        body = json.loads(request.data.decode('utf-8'))
        received, auth_info = Receive.parse_body(body)
        return Receive.handle_reply(received, auth_info)

    @staticmethod
    def handle_reply(received: dict, auth_info: dict) -> str:
        """
        Given a received message (parsed by `parse_body`), this function will reply the message
        by calling DingTalk API.
        """
        user_id: str = received['senderId']
        message_parts: list[str] = received['msg'].strip().split(' ')

        if len(message_parts) < 1:
            return Receive.send_msg(msg='蛤?', msg_key='sampleMarkdown', auth_info=auth_info)
        elif message_parts[0] == '在吗':
            return Receive.send_msg(msg=Receive.reply_msg[random.randint(0, len(Receive.reply_msg) - 1)],
                                    msg_key='sampleMarkdown',
                                    auth_info=auth_info)
        try:
            service = SERVICES_MAP[message_parts[0]]
        except KeyError:
            return Receive.send_msg(msg='We currently do not support this kind of service',
                                    msg_key='sampleMarkdown',
                                    auth_info=auth_info)
        else:
            service.load_config(Receive.configs)
            # TODO: support other types of messages
            return Receive.send_msg(msg=service.process_query(message_parts, user_id),
                                    msg_key='sampleMarkdown',
                                    auth_info=auth_info)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    MediumService.init_service(Receive.send_feedcard_msg, Receive.configs)
    scheduler = MediumService.create_scheduler()
    scheduler.start()

    Receive.app.run('0.0.0.0', 60001)
