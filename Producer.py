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
        print("id = {0} before: {1}\n".format(self.getIdent(), self.getNumerOfElementsOnStock()))
        while(self.getNumerOfElementsOnStock() == buffSize): self.wait("FULL")
        print("id = {0} is producing...\n".format(self.getIdent()))
        time.sleep(sleep_time)
        self.putElementOnStock()
        print("id = {0} after: {1}\n".format(self.getIdent(), self.getNumerOfElementsOnStock()))
        self.signalAll("EMPTY")
        self.exitCS()
