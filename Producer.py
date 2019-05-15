from Monitor import Monitor
import time
import random

class Producer(Monitor):
    def __init__(self):
        Monitor.__init__(self)
    
    def produce(self, buffSize):
        sleep_time = random.randint(1,3)
        time.sleep(sleep_time)
        self.enterCS()
        print("before: {0}\n".format(self.getNumerOfElementsOnStack()))
        while(self.getNumerOfElementsOnStack() == buffSize): self.wait("FULL")
        print("rank: {0} is producing...\n".format(self.ident))
        self.putElementOnStack()
        print("after: {0}\n".format(self.getNumerOfElementsOnStack()))
        self.signalAll("EMPTY")
        self.exitCS()
