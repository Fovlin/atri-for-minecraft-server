## plaese run pip install openai
import os
import json
import time
import socket
from openai import OpenAI

LATEST_LOG_PATH = "./logs/latest.log" # 你的服务器日志路径
API_KEY = "" # 你的 API 密钥
PASSWD = "" # 你的 RCON 密码
BASE_URL = "https://api.deepseek.com" # 根据实际情况替换，如果换成 deepseek 以外的模型，手动修改 48 行

sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client = OpenAI(api_key=API_KEY,base_url=BASE_URL)

# 发送登录数据包的方法
def socket_login():
    passwd = PASSWD.encode('utf-8')
    len_pack = (len(passwd) + 11).to_bytes(4,byteorder="little",signed=True)
    sc.send(len_pack + b"\x01\x00\x00\x00" + b"\x03\x00\x00\x00" + passwd + b"\x00\x00\x00")
    res = sc.recv(1024)
def heartbeat():
    try:
        socket_login()
    except:
        print(">>> 连接断开，尝试重新建立连接...")
        while True:
            try:
                global sc
                sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sc.connect(('localhost',25575))
                socket_login()
                print(">>> 重新建立连接！")
                break
            except Exception:
                time.sleep(2)
                pass
# 发送指令数据包的方法
def socket_send(command):
    command = command.encode('utf-8')
    bytes_len = (len(command) + 11).to_bytes(4,byteorder="little",signed=True)
    sc.send(bytes_len + b"\x02\x00\x00\x00" + b"\x02\x00\x00\x00" + command + b"\x00\x00\x00")
    sc.recv(1024)

# 读取并写入特定长度的日志以及用户消息的方法
def read_write_chat_log(UserMessage,context):
    with open(LATEST_LOG_PATH,'r') as file:
        all_log = str(file.readlines()[-32:]).strip('[]')
    context[1] = {"role": "system", "content": "最近的服务器日志：" + all_log}
    data1={"role": "user", "content":UserMessage} # 写入用户消息
    context.append(data1)
    return(context)

def main():
    
    old_last_line="x"

    if os.path.exists(LATEST_LOG_PATH) == True:
        print(">>> 锁定日志文件，开始监听...")

    else:
        print(">>> 无法锁定日志文件，情检查日志文件路径是否正确")       
        exit()     

    while True:

        heartbeat()

        # 读取最后一行
        with open(LATEST_LOG_PATH,'r') as file:
            last_line = None
            for line in file:
                last_line = line.strip()
            try:
                key = last_line[-3:]
            except:
                pass

        if key == ">>>":

            if last_line != old_last_line:

                print(">>> 命中检索词！")

                print(last_line)

                with open('chat.json','r') as file:
                    context = json.load(file)

                old_last_line = last_line # 将本次的日志传递给锁，防止同日志触发机器人回复

                context = read_write_chat_log(UserMessage=last_line,context=context)

                # openai 模块

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=context,
                    stream=False,
                    temperature=1,
                    #max_tokens=8192
                )

                # 写入 ai 回复消息
                data2 = {"role": "assistant", "content": response.choices[0].message.content}
                context.append(data2)

                # 控制 json 文件长度，防止我的 token 爆炸，你可以自定义长度。
                chat_len=len(context)
                if chat_len >= 64:
                    del context[2:6]

                # 将对话列表重新写入 json 文件
                with open('chat.json','w') as file:
                    json.dump(context,file,ensure_ascii=False,indent=4)

                TEXT = response.choices[0].message.content
                print("[ATRI] " + TEXT)
                socket_send(command="tellraw @a [{text:\"[ATRI] \",color:\"aqua\"},{text:\"" + TEXT + "\",color:\"white\"}]")

            else:
                time.sleep(2)
        else:
            time.sleep(2)

sc.connect(('localhost',25575))

print(">>> 建立连接")

socket_login()

print(">>> 登录数据包已发送")

main()