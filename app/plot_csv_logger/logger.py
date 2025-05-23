import os
import time
ROOT_DIR=os.path.dirname(os.path.abspath(__file__))
class Logger:
    
    @staticmethod
    def error(e):
        with open(os.path.join(ROOT_DIR,"log.txt"),"a") as f:
            f.write(f"\n {time.time()}; Error ; {e}")

    @staticmethod
    def info(e):
        with open(os.path.join(ROOT_DIR,"log.txt"),"a") as f:
            f.write(f"\n {time.time()}; Info ; {e}")