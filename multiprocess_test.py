from multiprocessing import Process
import os
import random
import time
# 子进程要执行的代码
def run_proc(name):
    time.sleep(random.randint(30,100)/100)
    print ('Run child process %s (%s)...' % (name, os.getpid()))


if __name__=='__main__':
    for i in range(10):
        print ('Parent process %s.' % os.getpid())
        p = Process(target=run_proc, args=('test',))
        p.start()
        p.join()

