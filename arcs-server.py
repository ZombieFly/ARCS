'''

Name: Alex remote control server
Version: v4.2
Last change time: 2020-8-28

Coding by Zombie_fly
Github: https://github.com/ZombieFly/ARCS

'''

from socket import *
import threading
import time
import json
import os,sys
import subprocess

key = '' #此处为远程控制发送信息前的验证密钥
flag = 1
flag2 = 0
_outputmsg = ''
lock = threading.Lock()

######################################################################################
def ctrlthread(process):
    global stop
    stop = 0
    while True:
        iput = input()
        if iput == 'alex stop':
            process.stdin.write(f'stop\n'.encode())
            process.stdin.flush()            
            stop = 1
            break
        process.stdin.write(f'{iput}\n'.encode())
        process.stdin.flush()

def title(msg,mtype='INFO',head='[ARCS]'):
    return f'{head}[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {mtype}]{msg}'

def output(process,lock,stop):
    global _outputmsg
    global flag2
    global flag
    while True:
        if stop == 1:
            break
        line = process.stdout.readline()
        lock.acquire()
        outputmsg = line.decode()
        if flag == 0:
            _outputmsg = f'{_outputmsg}{outputmsg}'
        if flag2 == 0:
            if 'Server started' in outputmsg:
                flag2 =1
        print(outputmsg.replace('\n',''))
        lock.release()

######################################################################################

print('Welcome to use the Alex remote control server v4.2')
#启动服务端
#bds_t = threading.Thread(target=bds)
#bds_t.setDaemon(True)
#bds_t.start()
process = subprocess.Popen("./bedrock_server", shell=False, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr=subprocess.STDOUT)

t3 = threading.Thread(target=ctrlthread,args=(process,))
t3.start()

#等待线程程序启动
#time.sleep(0.5)
#开启终端输出线程
t = threading.Thread(target=output,args=(process,lock,stop,))
t.setDaemon(True)
t.start()
print(f'Thread of output start:{t.is_alive()}')
print(f'Thread of ctrlthread start:{t3.is_alive()}')

while True:
    if flag2 == 1:
        break

################################
#  Alex remote control server  #
################################
#启用tcp监听
tcp_server_socket = socket(AF_INET, SOCK_STREAM)
address = ('', 8001)
tcp_server_socket.bind(address)
print(title('Successfully establish the socket','INFO'))

while True:
    tcp_server_socket.listen(5)
    print(title('Start listening','INFO'))

    client_socket, clientAddr = tcp_server_socket.accept()
    recv_data = client_socket.recv(1024)
    print(title('Connected'))
    try:
        g_key = recv_data.decode()
        if g_key == key:
            print(title('Key verification passed','INFO'))
            #从客户端接收信息
            recv_data = client_socket.recv(1024)
            msg = f'{recv_data.decode()}\n'
            #输入指令
            print(title(msg,'INPUT'))
            
            _outputmsg = ''
            flag = 0
            num = 0

            process.stdin.write(msg.encode())
            process.stdin.flush()
            #常规时延1s
            time.sleep(1)
            #延迟等待
            while True:
                if not _outputmsg and num <= 2:
                    num += 1
                    time.sleep(1)
                else:
                    if not _outputmsg:
                        ret = 'The input was successful, but the terminal did not return within the required time.'
                        print(title(ret,'WARNING'))
                        _outputmsg = ret
                    break
            flag = 1
            #发送终端信息
            client_socket.send(_outputmsg[:-1].encode())
        elif key == 'close the model right now':
            print(title('Get a close command','ARCS-CMD'))
            t.join(2)
            t2.join(2)
            break
        else:
            print(title('Key error,access denied','WARNING'))
            client_socket.send('Key error'.encode('gbk'))
    except:
        print(title('Data exchange failed','ERROR'))

    #按时close好习惯
    client_socket.close()
    print(title('Closed the socket'))
