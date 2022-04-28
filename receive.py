import json
import random
import socket
import time
import datetime
from threading import Thread
import requests
import Leetcode
import Question
from DDLService import DDLService
from UserOperation import UserOperation
from multi_func_reply import Search

ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(('127.0.0.1', 5701))
ListenSocket.listen(100)
bot_qq_account = 3292297816  # st_bot: 2585899559  # bot: 3292297816

HttpResponseHeader = '''HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n\r\n
'''


def send_msg(resp_dict):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip = '127.0.0.1'
    client.connect((ip, 5700))

    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息

    # 将字符中的特殊字符进行url编码
    msg = msg.replace(" ", "%20")
    msg = msg.replace("\n", "%0a")

    if msg_type == 'group':
        payload = "GET /send_group_msg?group_id=" + str(
            number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + ip + ":5700\r\nConnection: close\r\n\r\n"
    elif msg_type == 'private':
        payload = "GET /send_private_msg?user_id=" + str(
            number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + ip + ":5700\r\nConnection: close\r\n\r\n"
    else:
        payload = ''
    print("发送" + payload)
    client.send(payload.encode("utf-8"))
    client.close()
    return 0


def request_to_json(msg):
    for i in range(len(msg)):
        if msg[i] == "{" and msg[-1] == "\n":
            return json.loads(msg[i:])
    return None


def rev_msg():  # json or None
    client, address = ListenSocket.accept()
    request = client.recv(4096).decode('utf-8', 'ignore')
    rev_json = request_to_json(request)
    client.sendall(HttpResponseHeader.encode(encoding='utf-8'))
    client.close()
    return rev_json


def check_scheduled_task():
    """
    This function stores scheduled tasks.
    """
    while True:
        # get current time in UTC+8
        curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        # 8:00 AM, show ddl today
        if curr_time.hour == 8 and curr_time.minute == 0:
            ddl_service = DDLService()
            send_msg({'msg_type': 'group', 'number': '705716007', 'msg':
                     f'大家早上好呀, 又是新的一天，来看看今天还有哪些ddl呢>_<\n{ddl_service.process_query("ddl today".split(" "), "0")}'})
            ddl_service.remove_expired_ddl()  # remove expired ddl timely
            time.sleep(60)

        time.sleep(20)  # allow some buffer time.


def get_data(text):
    # 请求思知机器人API所需要的一些信息
    data = {
        "appid": "a612dbe7965b53eeb5eaf26edccc8c94",
        "userid": "sKJAeMs3",
        "spoken": text,
    }
    return data


def get_answer(text):
    # 获取思知机器人的回复信息
    data = get_data(text)
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


def rev_private_msg(rev):
    if rev['raw_message'] == '在吗':
        qq = rev['sender']['user_id']
        send_msg({'msg_type': 'private', 'number': qq, 'msg': reply_msg[random.randint(0, len(reply_msg) - 1)]})
    elif rev['raw_message'] == '你在哪':
        qq = rev['sender']['user_id']
        send_msg({'msg_type': 'private', 'number': qq, 'msg': '我无处不在'})
    elif rev['raw_message'].split(' ')[0] == '歌词':
        qq = rev['sender']['user_id']
        if len(rev['raw_message'].split(' ')) < 2:
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '请输入：歌曲<空格><歌曲名>来获得歌曲链接哦'})
        else:
            song = rev['raw_message'].replace('歌词', '')
            d = Search()
            music_id = d.search_song(song)
            if music_id is None:
                send_msg(
                    {'msg_type': 'private', 'number': qq, 'msg': '呜呜呜人家找不到嘛，换首歌试试吧'})
            else:
                text = Search.get_lyrics(music_id)
                send_msg(
                    {'msg_type': 'private', 'number': qq, 'msg': text})
    elif rev['raw_message'].split(' ')[0] == '歌曲':
        qq = rev['sender']['user_id']
        if len(rev['raw_message'].split(' ')) < 2:
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '请输入：歌曲<空格><歌曲名>来获得歌曲链接哦'})
        else:
            song = rev['raw_message'].replace('歌曲', '')
            d = Search()
            music_id = d.search_song(song)
            if music_id is None:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '呜呜呜人家找不到嘛，换首歌试试吧'})
            else:
                send_msg({'msg_type': 'private', 'number': qq, 'msg': '[CQ:music,type=163,id={}]'.format(music_id)})
    else:
        qq = rev['sender']['user_id']
        content = rev['raw_message']
        if content == '':
            answer = '根本搞不懂你在讲咩话，说点别的听听啦'
        else:
            answer = get_answer(content)
        send_msg({'msg_type': 'private', 'number': qq, 'msg': answer})


def rev_group_msg(rev):
    group = rev['group_id']
    if f'[CQ:at,qq={bot_qq_account}]' in rev["raw_message"]:
        qq = rev['sender']['user_id']
        message_parts = rev['raw_message'].split(' ')
        if message_parts[1] == '在吗':
            send_msg({'msg_type': 'group', 'number': group, 'msg': reply_msg[random.randint(0, len(reply_msg) - 1)]})
            # send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:poke,qq={}]'.format(qq)})
        elif message_parts[1] == '题来':
            question = Question.Question("2022/03/01", "1. 两数之和", "two_sum", "https://....", "简单", "哈希表，二分查找",
                                         {"enor2017": "Accepted", "nidhogg_mzy": ""})
            send_msg({'msg_type': 'group', 'number': group, 'msg': question.toString()})
        # code for daily sign
        elif message_parts[1] == 'today':
            # if user name is not provided the user must have been registered, otherwise, report error
            if len(rev['raw_message'].split(' ')) < 3:
                user_op = UserOperation()
                status_, username_ = user_op.get_leetcode(str(qq))
                if not status_:
                    send_msg({'msg_type': 'group', 'number': group, 'msg':
                              '我还不知道您的LeetCode账户名哦，试试 register <your leetcode username>, 或者在today 后面加上你要查找的用户名哦!'})
                    return
                username = username_
            # otherwise, we should get user name from user input
            else:
                username = rev['raw_message'].split(' ')[2]
            leetcode = Leetcode.Leetcode(username)
            res = leetcode.check_finish_problem('binary-search')
            # TODO: this is not complete, no message reply
        # check if today's problem has already completed
        elif message_parts[1] == 'check':
            # if user name is not provided, the user must have been registered, otherwise, report error
            if len(rev['raw_message'].split(' ')) < 3:
                user_op = UserOperation()
                status_, username_ = user_op.get_leetcode(str(qq))
                if not status_:
                    send_msg({'msg_type': 'group', 'number': group, 'msg':
                              '我还不知道您的LeetCode账户名哦，试试 register <your leetcode username>, 或者在check 后面加上你要查找的用户名哦!'})
                    return
                username = username_
            # otherwise, we should get user name from user input
            else:
                username = rev['raw_message'].split(' ')[2]
            leetcode = Leetcode.Leetcode(username)
            res = leetcode.check_finish_problem('binary-search')
            if not res:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '你怎么没写完啊？坏孩子！'})
            else:
                send_msg({'msg_type': 'group', 'number': group, 'msg': f'You have passed this problem '
                                                                       f'in the following languages: {res}'})
        # register: match the qq account with leetcode username,
        # so user don't need to provide username when query
        elif message_parts[1] == 'register':
            # if username is not provided
            if len(message_parts) < 3:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '正确食用方法: register <your leetcode username>'})
            else:
                user_op = UserOperation()
                _, msg_ = user_op.register(str(qq), message_parts[2])
                send_msg({'msg_type': 'group', 'number': group, 'msg': msg_})
        # check username, for already registered users
        elif message_parts[1] == 'username':
            user_op = UserOperation()
            status_, username_ = user_op.get_leetcode(str(qq))
            if not status_:
                send_msg({'msg_type': 'group', 'number': group,
                          'msg': '我还不知道您的LeetCode用户名诶，要不要试试 register <your leetcode username>'})
            else:
                send_msg({'msg_type': 'group', 'number': group,
                          'msg': f'您已绑定LeetCode的用户名是: {username_}'})
        # DDL Service
        elif message_parts[1] == 'ddl':
            service = DDLService()
            send_msg({'msg_type': 'group', 'number': group,
                      'msg': f"[CQ:at,qq={qq}]\n" + service.process_query(message_parts[1:], qq)})
        else:
            content = ""
            for i in range(1, len(message_parts)):
                content += message_parts[i] + " "
            send_msg({'msg_type': 'group', 'number': group, 'msg': f'[CQ:at,qq={qq}]' + get_answer(content)})


def message_process_tasks():
    """
    All private/group message processing are done here.
    """
    while True:
        received = rev_msg()
        try:
            if received["post_type"] == "message":
                # PRIVATE MESSAGE
                if received["message_type"] == "private":
                    rev_private_msg(received)
                # GROUP MESSAGE
                elif received["message_type"] == "group":
                    rev_group_msg(received)
        except TypeError:
            # This error will be reported to developers via qq private message.
            error_msg = f'[Internal Error] TypeError while doing "received["post_type"]", ' + \
                        f'where "received" is None. If the message received is too long, try ' + \
                        f'release the length restriction. (currently 4096)'
            send_msg({'msg_type': 'private', 'number': '2220038250', 'msg': error_msg})
            send_msg({'msg_type': 'private', 'number': '3429582673', 'msg': error_msg})
            # also record in log
            print(f'##### Error\n{error_msg}')


if __name__ == '__main__':
    # add a thread to check scheduled tasks
    trd_scheduled = Thread(target=check_scheduled_task)
    trd_scheduled.start()

    # add a thread to process message reply tasks
    trd_msg_reply = Thread(target=message_process_tasks)
    trd_msg_reply.start()
