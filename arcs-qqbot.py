from nonebot import on_command, CommandSession
from nonebot.message import unescape
from nonebot import on_natural_language, NLPSession, IntentCommand

import re
from socket import *

key = '' #此处为发送密钥，请确保与服务端填写的密钥一致
server_port = 8001
op_nums = [] #此处为允许通过机器人控制的管理qq号,为list变量

server_ip = '' #此处为bds ip

@on_command('trl',only_to_me=False)
async def trl(session: CommandSession):
    msg=session.current_arg_text.strip()
    qqnum=str(session.ctx['user_id'])
    if qqnum in op_nums:
        else:
            try:
                tcp_client_socket = socket(AF_INET, SOCK_STREAM)
                tcp_client_socket.settimeout(5)
                tcp_client_socket.connect((server_ip, server_port))
                print('连接成功')
                #发送验证
                tcp_client_socket.send(key.encode())
                #发送执行命令
                tcp_client_socket.send(msg.encode())
                recvData = tcp_client_socket.recv(1024)
                rtn = recvData.decode()
                await session.send(rtn)
                tcp_client_socket.close()
            except:
                await session.send('与服务器通信失败')

    else:
        await session.send('权限不足')
