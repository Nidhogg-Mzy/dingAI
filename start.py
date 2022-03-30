import receive
import sendMSG

while True:
    rev = receive.rev_msg()
    if rev["post_type"] == "message":
        print(rev) #需要功能自己DIY
        if rev["message_type"] == "private":  # 私聊
            if rev['raw_message'] == 'hello':
                qq = rev['sender']['user_id']
                sendMSG.send_msg({'msg_type': 'private', 'number': qq, 'msg': '我在'})
        elif rev["message_type"] == "group":  # 群聊
            group = rev['group_id']
            if "[CQ:at,qq=2585899559]" in rev["raw_message"]:
                if rev['raw_message'].split(' ')[1] == '在吗':
                    qq = rev['sender']['user_id']
                    sendMSG.send_msg({'msg_type': 'group', 'number': group, 'msg': '[CQ:poke,qq={}]'.format(qq)})
        else:
            continue
    else:  # rev["post_type"]=="meta_event":
        continue

