## plaese run pip install openai mcrcon

import json
import time
from mcrcon import MCRcon
from openai import OpenAI

API_KEY = "" # 你的 API 密钥
HOST = "127.0.0.1"
PASSWD = "" # 你的密码
BASE_URL = "https://api.deepseek.com" # 根据实际情况替换，如果换成 deepseek 以外的模型，手动修改 48 行

mcr = MCRcon(HOST,PASSWD)

mcr.connect()

old_log="x"

while True:

    # 读取最后一行
    with open('./logs/latest.log','r',encoding='utf-8') as file:
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
                temperature=1.3,
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
        
            resp = mcr.command("/tellraw @a [{text:\"[ATRI] \",color:\"aqua\"},{text:\"" + TEXT + "\",color:\"white\"}]")

            print(resp)

        else:
            time.sleep(1)
    else:
        time.sleep(3)