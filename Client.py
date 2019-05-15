from Monitor import Monitor
import time
import random

class Client(Monitor):
    def __init__(self):
        Monitor.__init__(self)
    
    def consume(self):
        sleep_time = random.randint(1,3)
        time.sleep(sleep_time)
        self.enterCS()
        print("before: {0}\n".format(self.getNumerOfElementsOnStack()))
        while(self.getNumerOfElementsOnStack() == 0): self.wait("EMPTY")
        print("rank: {0} is consuming..\n".format(self.ident))
        self.popElementFromStack()
        print("after: {0}\n".format(self.getNumerOfElementsOnStack()))
        self.signalAll("FULL")
        self.exitCS()