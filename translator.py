import requests_html
from requests_html import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import  itchat
itchat.auto_login(True)
import difflib,os
from itchat.content import TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, ATTACHMENT, VIDEO, FRIENDS, SYSTEM
# 下载文件到本地
import shutil
from cut import *

def download_files(msg):
    msg.download(msg['FileName'])
    shutil.move(msg['FileName'],'./listen/1.mp3')

@itchat.msg_register([TEXT,MAP,CARD,NOTE,SHARING,PICTURE,RECORDING,ATTACHMENT,VIDEO,FRIENDS,SYSTEM])
def reply_mseeage(msg):
    if msg['Type'] == TEXT:
        replyContent="我收到了文本消息"
        #download_files(msg)
    if msg['Type'] == RECORDING:
        replyContent = "我收到了语音"
        download_files(msg)
        return change()

   

def translate(content):
    ret = ''
    r = requests.get('https://dictionary.cambridge.org/zhs/词典/英语-汉语-简体/'+content)
    code = r.text
    #print(code)
    left = code.find('<span class="trans dtrans dtrans-se " lang="zh-Hans">')
    soup = BeautifulSoup(code,'html.parser')
    for i in soup.find_all('span',attrs={"lang": "zh-Hans",'class':'trans dtrans dtrans-se '}):
        ret += str(i.string)+'\n'
    return ret

@itchat.msg_register([itchat.content.TEXT], isGroupChat=True)
def listening(msg):
    if msg['isAt']:
        print(msg['Content'])
        ret = msg['Content']
       #print(msg['UserName'])
        ret = ret.split()
        ret = ret[len(ret)-1]
        return translate( ret)
  
itchat.run()