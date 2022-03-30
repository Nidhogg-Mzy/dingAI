import socket
import json
import random
import Leetcode
import Question

ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(('127.0.0.1', 5701))
ListenSocket.listen(100)

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
    Client, Address = ListenSocket.accept()
    Request = Client.recv(1024).decode(encoding='utf-8')
    rev_json = request_to_json(Request)
    Client.sendall(HttpResponseHeader.encode(encoding='utf-8'))
    Client.close()
    return rev_json


def rev_private_msg(rev):
    if rev['raw_message'] == '在吗':
        qq = rev['sender']['user_id']
        randomnum1 = random.randint(0, 3)
        if randomnum1 == 0:
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '在的呀小可爱'})
        elif randomnum1 == 1:
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '一直在的呀'})
        else:
            send_msg({'msg_type': 'private', 'number': qq, 'msg': '呜呜呜找人家什么事嘛'})
    if rev['raw_message'] == '你在哪':
        qq = rev['sender']['user_id']
        send_msg({'msg_type': 'private', 'number': qq, 'msg': '我无处不在'})
    else:
        qq = rev['sender']['user_id']
        send_msg({'msg_type': 'private', 'number': qq, 'msg': rev['raw_message']})


def rev_group_msg(rev):
    group = rev['group_id']
    if "[CQ:at,qq=2585899559]" in rev["raw_message"]:
        if rev['raw_message'].split(' ')[1] == '在吗':
            index = random.randint(0, 3)
            if index == 0:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '在的呀小可爱'})
            elif index == 1:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '一直在的呀'})
            else:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '呜呜呜找人家什么事嘛'})
            # send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:poke,qq={}]'.format(qq)})
        elif rev['raw_message'].split(' ')[1] == '题来':
            question = Question.Question("2022/03/01", "1. 两数之和", "two_sum", "https://....", "简单", "哈希表，二分查找",
                                         {"enor2017": "Accepted", "nidhogg_mzy": ""})
            send_msg({'msg_type': 'group', 'number': group, 'msg': question.toString()})
        # code for daily sign
        elif rev['raw_message'].split(' ')[1] == 'today':
            send_msg({'msg_type': 'group', 'number': group, 'msg': 'testing today'})
            # if user name is not provided
            if len(rev['raw_message'].split(' ')) < 3:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '请提供LeetCode账户名'})
            # get user name from user input
            else:
                username = rev['raw_message'].split(' ')[2]
                leetcode = Leetcode.leetcode(username)
        # check if already completed
        elif rev['raw_message'].split(' ')[1] == 'check':
            # if user name is not provided
            if len(rev['raw_message'].split(' ')) < 3:
                send_msg({'msg_type': 'group', 'number': group, 'msg': '请提供LeetCode账户名'})
            # get user name from user input
            else:
                username = rev['raw_message'].split(' ')[2]
                print(username)
                leetcode = Leetcode.Leetcode(username)
                res = leetcode.check_finish_problem('binary-search')
                if not res:
                    send_msg({'msg_type': 'group', 'number': group, 'msg': '你怎么没写完啊？坏孩子！'})
                else:
                    send_msg({'msg_type': 'group', 'number': group, 'msg': f'You have passed this problem '
                                                                           f'in the following languages: {res}'})


if __name__ == '__main__':
    while True:
        received = rev_msg()
        if received["post_type"] == "message":
            # PRIVATE MESSAGE
            if received["message_type"] == "private":
                rev_private_msg(received)
            # GROUP MESSAGE
            elif received["message_type"] == "group":
                rev_group_msg(received)
            else:
                continue
        else:  # rev["post_type"]=="meta_event":
            continue
