import requests_html
from requests_html import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from multiprocessing import Process,Pipe,Pool
import numpy as np
import redis
#redis_conn = redis.Redis(host='127.0.0.1', port= 6379, password= '', db= 0)

class node:
    def init(self):
        self.key = ''
        self.val = 0
        pass

def search(content,conn):
    strtmp = [
        '<span class="epp-xref dxref A1">A1</span>',
        '<span class="epp-xref dxref A2">A2</span>',
        '<span class="epp-xref dxref B1">B1</span>',
        '<span class="epp-xref dxref B2">B2</span>',
        '<span class="epp-xref dxref C1">C1</span>',
        '<span class="epp-xref dxref C2">C2</span>'
    ]
    r = requests.get('https://dictionary.cambridge.org/zhs/词典/英语-汉语-简体/'+content)
    code = r.text
    s = -1
    level = 0
    for i in strtmp:
        s = code.find(i)
        level+=1
        if s != -1:
            break
    key = content
    val = level
    #conn.set(key,val)
    return [key,val]

def judgment(wordlist):
    wordlist = list(set(wordlist))
    redis_conn = 0
    p = Pool()
    result = []
    for i in wordlist:
        result.append(p.apply_async(search, args=(i,redis_conn)).get())
    p.close()
    p.join()
    score_average = 0
    for i in result:
        score_average += i[1]
    
    score_average = score_average/len(result)
    change = score_average / 6 * 10
    #print(change)
    #print(score_average)
    return change
if __name__ == '__main__':
    judgment(list(set(['uh','summary','soar'])))

#两分钟要能够表达150-200词的为5分段
#200-220的为5.5分或者6分段
#220-250为6.5分段
#250-270的为7分段
#270-300的为7.5或者8分段
#超越300的直接9分

