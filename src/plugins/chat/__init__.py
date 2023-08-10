import json
from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.adapters import Event
import requests
import re       #字符串匹配模块

def load_database(filename):
    """加载题库"""
    database = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line.replace("：",":")
            parts = line.strip().split(':')
            if len(parts) == 2:
                question = parts[0].strip()
                answer = parts[1].strip()
                database[question] = answer
    return database

def update_database(file_name, dic, question, answer):
    """更新数据库"""
    dic[question] = answer
    with open(file_name, 'w', encoding='utf-8') as file:
        for q, a in dic.items():
            file.write(f"{q}: {a}\n")
    return dic

def check_bad_word(input_string):
    sensitive_words = ["你妈", "傻逼", "xxx"]  # 添加其他敏感词汇
    for word in sensitive_words:
        if word in input_string:
            return True
    return False

"""2023.8.9
信息以@小智 开头时应答
1.@小智，帮我查查    ----调用gpt
2.
default:使用青云API智能问答
"""

pattern_search = re.compile(r"^帮我查查\s*(.*)$")

chatgpt = on_command("",rule=to_me(), aliases={
                     "gpt", "chatgpt"}, priority=10, block=True)

@chatgpt.handle()
async def handle_function(event: Event): 
    database_name = 'database.txt'
    database = load_database(database_name)
    text="大家好，我是小智，使用none-bot框架搭建的服务于智能工程学院迎新工作的聊天机器人。我可以和大家聊天，解答大家入学的相关疑问，也可以提供基于“通义千问”语言大模型的搜索服务\n"
    menu="这是我的使用方法:\n@小智 帮我查查+内容，我会帮你在“通义千问”中帮你搜索\n@小智 问题库-->列出已有问题\n@小智-->在线聊骚\n@学长学姐-->能解答我解答不了的问题  QAQ"
    message = event.get_plaintext()
    print(message)
    if message:
        query=re.sub(r'[!()-\[\]{};:\'",，<>./?@#$%^&*_~]', '', message).strip("怎样")  #去除所有标点符号
        # 1.匹配GPT指令:    #帮我查查
        match_search=pattern_search.match(message.strip('，, '))
        if  match_search :
            await chatgpt.send("收到，稍等~")
            query = match_search.group(1)  #提取查询内容
            text = requestGPTApi(query)
            await chatgpt.finish(text)
        #2.自我介绍
        elif "自我介绍" in message or "你是谁" in message or "介绍一下自己" in message:
            await chatgpt.send(text)
            await chatgpt.finish(menu)
        #3.题库补充
        elif "有人问你" in message and ("你就答" in message or "你就说" in message):
            message=message.replace("你就说","你就答")
            message=message.strip().replace("有人问你",'').split('你就答')  #掐头
            Q=message[0].split("/") #Q去除所有标点符号，方便泛化
            for q in Q:
                q=re.sub(r'[!()-{};:，,<>.?@#$%^&*_~]', '', q).strip(',').strip('，')
                A=message[1].strip(",").strip("，")
                database=update_database(database_name,database,q,A)
            await chatgpt.finish("知道了！")
        #4.数据库查询
        elif query in database :
            text=database[query]
            await chatgpt.finish(text)
        elif "重载数据库" in message:
            database = load_database(database_name)
            await chatgpt.finish("遵命！")
        #5.列出题单
        elif "问题库" in message or "数据库" in message or "题库" in message or "看看问题" in message:
            text=""
            for i in database.keys():
                text+=("-"+i+"\n")
            if text=='':
                await chatgpt.finish("完蛋，题库没了，有人删库了T_T！！！快去喊我爹！")
                return
            await chatgpt.finish(text)
        #粗口屏蔽
        elif check_bad_word(message):
            text="你是不是在骂我...我蠢，你可别欺负我Q_Q"
            await chatgpt.finish(text)
        #其他：使用智能问答
        else:
            text = autoReply(message)
            text=text.replace("菲菲","小智")
            if check_bad_word(text):
                text="一股神秘力量封住了小智的嘴(我爆粗被阻止了)"
            await chatgpt.finish(text)
    return


def autoReply(msg):
    target=f'http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}'
    req=requests.get(url=target)
    response_json=req.text
    print(response_json)
    response_json=json.loads(response_json)
    content=response_json["content"]
    return content

def requestGPTApi(msg):
    response = requests.get('http://127.0.0.1:8000/chat-api/?msg='+msg)
    result = json.loads(response.text)
    text = result['text']
    return text


