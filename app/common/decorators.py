import time
class Decorators:
    
    @staticmethod
    def FPS(function):
        def wrapper(*args,**kwags):
            startTime= time.perf_counter()
            function(*args,**kwags)
            endTime= time.perf_counter()
            print(round(1/(endTime-startTime)))
        return wrapper
    
    @staticmethod
    def TIME(function):
        def wrapper(*args,**kwags):
            startTime= time.perf_counter()
            function(*args,**kwags)
            endTime= time.perf_counter()
            print(endTime-startTime)
        return wrapper



