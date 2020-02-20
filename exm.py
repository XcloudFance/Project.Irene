import  itchat
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
        download_files(msg)
    if msg['Type'] == RECORDING:
        replyContent = "我收到了语音"
        download_files(msg)
        return change()

   
    return replyContent;
    
itchat.auto_login(hotReload=True)
itchat.run()