## plaese run pip install openai
import json
import time
import socket
from openai import OpenAI

LOG_PATH = "./logs/latest.log" # 你的服务器日志路径
API_KEY = "" # 你的 API 密钥
HOST = "127.0.0.1"
PASSWD = "" # 你的密码
BASE_URL = "https://api.deepseek.com" # 根据实际情况替换，如果换成 deepseek 以外的模型，手动修改 48 行

sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sock_start():
    sc.connect(('localhost',25575))
    passwd = PASSWD.encode('utf-8')
    len_pack = (len(passwd) + 11).to_bytes(4,byteorder="little",signed=True)
    sc.send(len_pack + b"\x01\x00\x00\x00" + b"\x03\x00\x00\x00" + passwd + b"\x00\x00\x00")
    sc.recv(1024)

def socket_send(command):
    command = command.encode('utf-8')
    bytes_len = (len(command) + 11).to_bytes(4,byteorder="little",signed=True)
    sc.send(bytes_len + b"\x02\x00\x00\x00" + b"\x02\x00\x00\x00" + command + b"\x00\x00\x00")
    sc.recv(1024)

sock_start()

old_log="x"

while True:

    # 读取最后一行
    with open(LOG_PATH,'r',encoding='utf-8') as file:
        log = file.readlines()[-1].strip("\n")
        key = log[-3:]

    if key == ">>>":

        if log != old_log:

            with open('chat.json','r') as file:
                context = json.load(file)

            UserMessage=log

            old_log=log
        
            data1={"role": "user", "content":UserMessage}

            context.append(data1)

            client = OpenAI(
                api_key=API_KEY,
                base_url=BASE_URL)

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=context,
                stream=False,
                temperature=0.7,
                max_tokens=5120
            )

            data2 = {"role": "assistant", "content": response.choices[0].message.content}

            context.append(data2)

            chat_len=len(context)

            # 控制 json 文件长度，防止我的 token 爆炸，你可以自定义长度。

            if chat_len >= 64:
                del context[1:5]

            with open('chat.json','w') as file:
                json.dump(context,file,ensure_ascii=False,indent=2)

            TEXT = response.choices[0].message.content

            socket_send(command="tellraw @a [{text:\"[ATRI] \",color:\"aqua\"},{text:\"" + TEXT + "\",color:\"white\"}]")

        else:
            time.sleep(1)
    else:
        time.sleep(3)

# =====================================================
#             一时兴起自学 Python 一天的成果
#  bug 满天飞，欢迎各位大佬随时批评指正（打字带括号是在调用函数吗
#
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.'_> '".
#         | | :  `- \`. ;`. _/ ; .-' / : | |
#         \  \ `-.   \_ __\ /__ _/   .-' /  /
#  ======`-.____`-.___\_____/___.-`____.-'============
#                       `=---='
#
#          佛祖保佑        无bug、不报错
# ====================================================
