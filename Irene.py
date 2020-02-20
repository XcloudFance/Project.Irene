from bs4 import BeautifulSoup
import itchat
import difflib, os
from random import randint
from itchat.content import (
    TEXT,
    MAP,
    CARD,
    NOTE,
    SHARING,
    PICTURE,
    RECORDING,
    ATTACHMENT,
    VIDEO,
    FRIENDS,
    SYSTEM,
)

# 下载文件到本地
from cut import *
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
import json, redis, sys, shutil
import requests_html
from requests_html import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from multiprocessing import Process, Pipe, Pool
import numpy as np
import threading
itchat.auto_login(True)
tester_queue = {"": ""}  # 这是一个测试者的队列
tester_score = {"": ""}
# 多线程如何返回值
class MyThread(threading.Thread):
 
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)
 
    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


def readtitle():
    part2 = []
    part3 = []
    f = open("./lib/part1.txt", "r")
    part1 = f.read().split("\n")
    f.close()
    f = open("./lib/part2/0.txt")
    part2.append(f.read())
    f.close()
    f = open("./lib/part3/0.txt")
    part3.append(f.read().split("\n"))
    f.close()
    f = open("./lib/perviously.txt")
    opening = f.read()
    f.close()
    return part1, part2, part3, opening


class node:
    def init(self):
        self.key = ""
        self.val = 0
        pass


def search(content, conn):
    strtmp = [
        '<span class="epp-xref dxref A1">A1</span>',
        '<span class="epp-xref dxref A2">A2</span>',
        '<span class="epp-xref dxref B1">B1</span>',
        '<span class="epp-xref dxref B2">B2</span>',
        '<span class="epp-xref dxref C1">C1</span>',
        '<span class="epp-xref dxref C2">C2</span>',
    ]
    r = requests.get("https://dictionary.cambridge.org/zhs/词典/英语-汉语-简体/" + content)
    code = r.text
    s = -1
    level = 0
    for i in strtmp:
        s = code.find(i)
        level += 1
        if s != -1:
            break
    key = content
    val = level
    # conn.set(key,val)
    return [key, val]


def judge_hard(wordlist):  # 判分单词难度
    wordlist = list(set(wordlist))
    redis_conn = 0
    t_list = []
    result = []
    for i in wordlist:
        if i != "":
            t_list.append(MyThread(search,args=(i, redis_conn)))
    for t in t_list:
        t.setDaemon(True)
        t.start()
    for t in t_list:
        t.join()
        result.append(t.get_result())
    score_average = 0
    for i in result:
        score_average += i[1]

    score_average = score_average / len(result)
    change = score_average / 6 * 10
    # print(change)
    # print(score_average)
    return change


class ColoredText:
    """Colored text class"""

    colors = ["black", "red", "green", "orange", "blue", "magenta", "cyan", "white"]
    color_dict = {}
    for i, c in enumerate(colors):
        color_dict[c] = (i + 30, i + 40)

    @classmethod
    def colorize(cls, text, color=None, bgcolor=None):
        """Colorize text
        @param cls Class
        @param text Text
        @param color Text color
        @param bgcolor Background color
        """
        c = None
        bg = None
        gap = 0
        if color is not None:
            try:
                c = cls.color_dict[color][0]
            except KeyError:
                print("Invalid text color:", color)
                return (text, gap)

        if bgcolor is not None:
            try:
                bg = cls.color_dict[bgcolor][1]
            except KeyError:
                print("Invalid background color:", bgcolor)
                return (text, gap)

        s_open, s_close = "", ""
        if c is not None:
            s_open = "\033[%dm" % c
            gap = len(s_open)
        if bg is not None:
            s_open += "\033[%dm" % bg
            gap = len(s_open)
        if not c is None or bg is None:
            s_close = "\033[0m"
            gap += len(s_close)
        return ("%s%s%s" % (s_open, text, s_close), gap)


def get_ginger_url(text):
    """Get URL for checking grammar using Ginger.
    @param text English text
    @return URL
    """
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"

    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.parse.urlencode(
        [("lang", "US"), ("clientVersion", "2.0"), ("apiKey", API_KEY), ("text", text)]
    )
    fragment = ""

    return urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))


def get_ginger_result(text):
    """Get a result of checking grammar.
    @param text English text
    @return result of grammar check by Ginger
    """
    url = get_ginger_url(text)

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        print("HTTP Error:", e.code)
        quit()
    except URLError as e:
        print("URL Error:", e.reason)
        quit()

    try:
        result = json.loads(response.read().decode("utf-8"))
    except ValueError:
        print("Value Error: Invalid server response.")
        quit()

    return result


def checker(original_text):
    """main function"""
    original_text

    fixed_text = original_text
    results = get_ginger_result(original_text)
    # Correct grammar
    if not results["LightGingerTheTextResult"]:
        return "No Wrong"

    # Incorrect grammar
    color_gap, fixed_gap = 0, 0
    for result in results["LightGingerTheTextResult"]:
        if result["Suggestions"]:
            from_index = result["From"] + color_gap
            to_index = result["To"] + 1 + color_gap
            suggest = result["Suggestions"][0]["Text"]

            # Colorize text
            gap = 0
            colored_incorrect = original_text[from_index:to_index]
            colored_suggest = suggest

            original_text = (
                original_text[:from_index]
                + colored_incorrect
                + original_text[to_index:]
            )
            fixed_text = (
                fixed_text[: from_index - fixed_gap]
                + colored_suggest
                + fixed_text[to_index - fixed_gap :]
            )

            color_gap += gap
            fixed_gap += to_index - from_index - len(suggest)
    return fixed_text


# 判断相似度的方法，用到了difflib库
def get_equal_rate_1(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


def grammarchecker(text):
    return checker(text)


def judge_grammar(text):
    total = 9
    a = text.split(".")
    for i in a:
        if i != "":
            b = grammarchecker(i)
            if b != "No Wrong":
                percentage = get_equal_rate_1(a, b)
                if percentage >= 95:
                    total -= 0.1
                if percentage < 95 and percentage >= 75:
                    total -= 0.2
                if percentage < 75:
                    total -= 0.4
                if total < 0:
                    total = 0
            else:
                total = 9
    return total


def judge_fluency(wordnum, length, type: int):
    if type == 1:  # 说明现在是part1部分
        percentage = wordnum / length
        # Attention:这边的length是以s为单位，也就是秒
    if type == 2:
        if length >= 120:
            if wordnum <= 150:
                return 5
            if wordnum <= 200:
                return 5.5
            if wordnum <= 220:
                return 6
            if wordnum <= 250:
                return 6.5
            if wordnum <= 280:
                return 7
            if wordnum <= 320:
                return 8
            if wordnum <= 350:
                return 7.5  # 这他妈的叫背诵我觉得
        else:
            return 1

def download_files(msg):
    msg.download(msg["FileName"])
    shutil.move(msg["FileName"], "./listen/1.mp3")

def detail_part1(wordlist,text,msg):
    global tester_score
    hard = judge_hard(wordlist)
    grammar = judge_grammar(text)
    tester_score[msg["FromUserName"]]["part1"] += (hard + grammar) / 2

def detail_part2(wordlist,text,msg):
    global tester_score
    hard = judge_hard(wordlist)
    filename = "./listen/1.mp3"
    mp3 = AudioSegment.from_mp3(filename)  # 打开mp3文件
    fluency = judge_fluency(len(wordlist), int(len(mp3)/1000), 2)
    grammar = judge_grammar(text)
    print(hard,grammar,fluency)
    tester_score[msg["FromUserName"]]["part2"] = (
        hard + grammar + fluency
    ) / 3

def detail_part3(wordlist,text,msg):
    global tester_score
    hard = judge_hard(wordlist)
    grammar = judge_grammar(text)
    tester_score[msg["FromUserName"]]["part3"] += (hard + grammar) / 2


Thread_TotalPart = []
@itchat.msg_register(
    [
        TEXT,  # 文本
        MAP,  # 地图
        CARD,  # 卡片
        NOTE,  # 笔记
        SHARING,  # 分享
        PICTURE,  # 图片
        RECORDING,  # 录音
        ATTACHMENT,  # 附件
        VIDEO,  # 视频
        FRIENDS,  # 好友请求
        SYSTEM,  # 系统消息
    ]
)
def reply_mseeage(msg):
    global part1, part2, part3, opening,tester_score
    print('1')
    #总结的时候要确保所有线程全部归位
    if msg["Type"] == TEXT:
        replyContent = "我收到了文本消息"
        content = msg["Content"]
        pos = 0
        # print(msg)
        if content == "Start":
            if msg["FromUserName"] in tester_queue:
                return "No Way!"
            else:
                tester_queue[msg["FromUserName"]] = 0
                tester_score[msg["FromUserName"]] = {}
                tester_score[msg["FromUserName"]]["part1"] = 0
                tester_score[msg["FromUserName"]]["part2"] = 0
                tester_score[msg["FromUserName"]]["part3"] = 0
            return opening
        if content == "Next" and msg["FromUserName"] in tester_queue:
            rate = tester_queue[msg["FromUserName"]]
            if rate == 0 or rate == 1 or rate == 2:
                tester_queue[msg["FromUserName"]] += 1
                tmp = randint(0, len(part1) - 1)
                val = part1[tmp]
                part1.remove(val)
                return val
            if rate == 3:
                tester_queue[msg["FromUserName"]] += 1
                tmp = randint(0, len(part2) - 1)
                pos = tmp
                val = part2[tmp]
                return val
            if rate == 4 or rate == 5:
                tester_queue[msg["FromUserName"]] += 1
                tmp = randint(0, len(part3[pos]) - 1)
                val = part3[pos][tmp]
                part3[pos].remove(val)
                return val
            if rate == 6:
                content = """
                You have talent for English! \n
                Here is your report:\n
                """
                for i in Thread_TotalPart:
                    i.join()
                
                p1 = tester_score[msg["FromUserName"]]["part1"] / 3
                content += "In part1, you got %.0f \n" % p1
                p2 = tester_score[msg["FromUserName"]]["part2"] 
                content += "In part2, you got %.0f \n" % p2
                p3 = tester_score[msg["FromUserName"]]["part3"] / 2
                content += "In part3, you got %.0f \n" % p3
                
                content += (
                    "Totally, Your credit of speaking is %.1f" %((p1 + p2 + p3) / 3)
                )
                # print(part1,part2,part3)
                return content

    if msg["Type"] == RECORDING:
        #global tester_score
        replyContent = "我收到了语音"
        if msg["FromUserName"] in tester_queue:
            download_files(msg)
            text = change()
            rate = tester_queue[msg["FromUserName"]]
            wordlist = (
                text.replace(",", "")
                .replace(".", "")
                .replace("!", "")
                .replace("?", "")
                .split(" ")
            )
            #print(wordlist)
            if rate == 1 or rate == 2 or rate == 3:  # part1
                t = MyThread(detail_part1,args=(wordlist,text,msg))
                t.setDaemon(True)
                Thread_TotalPart.append(t)
                t.start()

            if rate == 4:  # part2
                username = msg['FromUserName']
                if not "part2_step" in tester_score[username]:
                    tester_score[username]["part2_step"] = 0
                    tester_score[username]['wordlist'] = wordlist
                    tester_score[username]['text'] = text
                    return 'Ok'
                else:
                    tester_score[username]["part2_step"] += 1
                    

                if tester_score[username]["part2_step"] >= 3:  # 结束后不允许再次发送录音
                    return "Part2 end."

                if (
                    tester_score[username]["part2_step"] == 2
                ):  # 第三段录音歧义太大，不判断
                    pass
                else:
                        tester_score[username]['wordlist'] += wordlist
                        tester_score[username]['text'] += text
                        return 'Ok'

                t = MyThread(detail_part2,args=(tester_score[username]['wordlist'] , tester_score[username]['text'] ,msg))
                t.setDaemon(True)
                Thread_TotalPart.append(t)
                t.start()
            if rate == 5 or rate == 6:  # part3
                t = MyThread(detail_part3,args=(wordlist,text ,msg))
                t.setDaemon(True)
                Thread_TotalPart.append(t)
                t.start()


def translate(content):
    ret = ""
    r = requests.get("https://dictionary.cambridge.org/zhs/词典/英语-汉语-简体/" + content)
    code = r.text
    # print(code)
    left = code.find('<span class="trans dtrans dtrans-se " lang="zh-Hans">')
    soup = BeautifulSoup(code, "html.parser")
    for i in soup.find_all(
        "span", attrs={"lang": "zh-Hans", "class": "trans dtrans dtrans-se "}
    ):
        ret += str(i.string) + "\n"
    return ret


@itchat.msg_register([itchat.content.TEXT], isGroupChat=True)
def listening(msg):
    if msg["isAt"]:
        print(msg["Content"])
        ret = msg["Content"]
        # print(msg['UserName'])
        ret = ret.split()
        ret = ret[len(ret) - 1]
        return translate(ret)


part1, part2, part3, opening = readtitle()
itchat.run()
