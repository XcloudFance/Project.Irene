from pydub import AudioSegment
import os, re
def change():
    os.system('cd ./listen & del pcm16k.pcm')
    os.system('ffmpeg -i ./listen/1.mp3 -f s16le -ar 16000 -ac 1 -acodec pcm_s16le ./listen/pcm16k.pcm')
    out = os.popen('cd ./listen & node iat-ws-node.js').read().strip()
    return out
# 循环目录下所有文件
def cut():
    filename = './listen/1.mp3'
    mp3 = AudioSegment.from_mp3(filename) # 打开mp3文件
    print(len(mp3))
    lenmp3 = len(mp3)/1000
    
    #mp3[60*1000:].export(filename, format="mp3") # 切割前17.5秒并覆盖保存
