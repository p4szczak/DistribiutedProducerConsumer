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
        print("id = {0} before: {1}\n".format(self.getIdent(), self.getNumerOfElementsOnStock()))
        while(self.getNumerOfElementsOnStock() == 0): self.wait("EMPTY")
        print("id = {0} is consuming..\n".format(self.getIdent()))
        self.popElementFromStock()
        print("id = {0} after: {1}\n".format(self.getIdent(), self.getNumerOfElementsOnStock()))
        self.signalAll("FULL")
        self.exitCS()