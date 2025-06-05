import os
import time
import datetime
ROOT_DIR=os.path.dirname(os.path.abspath(__file__))

class Logger:
    
    @staticmethod
    def error(e):
        dateTime=datetime.datetime.fromtimestamp(time.time())
        with open(os.path.join(ROOT_DIR,"log.txt"),"a") as f:
            f.write(f"\n {dateTime.strftime('%Y-%m-%d %H:%M:%S')}; Error ; {e}")

    @staticmethod
    def info(e):
        dateTime=datetime.datetime.fromtimestamp(time.time())
        with open(os.path.join(ROOT_DIR,"log.txt"),"a") as f:
            f.write(f"\n {dateTime.strftime('%Y-%m-%d %H:%M:%S')}; Info ; {e}")