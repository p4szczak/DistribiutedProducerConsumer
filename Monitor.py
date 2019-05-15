from mpi4py import MPI
from Token import Token
from collections import deque
from enum import Enum
import logging
import threading
import time


# enum
class MsgType(Enum):
    REQUEST = 1
    TOKEN = 2
    KILL = 3

class Request:
    def __init__(self, ident, seqNo):
        self.ident = ident
        self.seqNo = seqNo


class Monitor:
    def __init__(self):
        self.comm = MPI.COMM_WORLD
        self.RN = [0] * self.comm.Get_size()
        self.hasToken = False
        self.inCS = False
        self.ident = self.comm.Get_rank()
        self.token = None
        

        self.actives = list(range(0,self.comm.Get_size()))

        self.mutex = threading.Lock()
        self.threadLive = True
        if(self.ident == 0):
            print("id = {0} initializing token\n".format(self.ident))
            self.token = Token([0] * self.comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True
        # self.stop_threads = False
        self.t1 = threading.Thread(target= self.recieverThread)
        self.t1.start()
        # t1.join()

    def kill(self):
        self.mutex.acquire()
        self.threadLive = False
        self.mutex.release()
        # self.actives.remove(self.ident)
        for i in self.actives:
            if i == self.ident: continue
            print("id = {0} sends info about dying\n".format(self.ident))
            req = Request(self.ident, -1)
            self.comm.isend(req, dest = i, tag = MsgType.KILL.value)

        self.t1.join()
        # self.token = None
        

        # while self.hasToken and len(self.actives) > 0:
        #     print("{0} {1}".format(self.hasToken, len(self.actives)))
            # self.comm.send(self.token, dest = self.actives[0], tag=MsgType.TOKEN.value)
        print("id = {0} is dead\n".format(self.ident))
    

    def enterCS(self):
        self.mutex.acquire()
        print("id = {0} trying to enter to CS\n".format(self.ident))
        
        if(not(self.hasToken)):
            self.sendRequest()
            info = MPI.Status()
            self.mutex.release()
            print("id = {0} is waiting for token\n".format(self.ident))
            tempToken = self.comm.recv(source = MPI.ANY_SOURCE, tag = MsgType.TOKEN.value, status = info)
            self.mutex.acquire()
            self.token = tempToken
            print("id = {0} recived token from: {1}\n".format(self.ident, info.source))
            self.hasToken = True
        print("id = {0} RN: {1} token-LN: {2}\n".format(self.ident, self.RN, self.token.LN))
        print("id = {0} is in CS\n".format(self.ident))
        self.inCS = True

        self.mutex.release()

    def sendRequest(self):
        self.RN[self.ident] += 1
        req = Request(self.ident, self.RN[self.ident])
        for i in self.actives:
            # print(type(i))
            
            print("id = {0} sending request to {1} with seq: {2}\n".format(self.ident, i, req.seqNo))
            if(self.ident == i): continue
            self.comm.isend(req, dest=i, tag=MsgType.REQUEST.value)
    
    def exitCS(self):
        self.mutex.acquire()
        print("id = {0} exit CS\n".format(self.ident))
        
        self.tokenTransfer()
        print("id = {0} RN: {1}\n".format(self.ident, self.RN))
        self.inCS = False
        self.mutex.release()
        

    def tokenTransfer(self):
        for i in self.actives:
            if self.RN[i] == self.token.LN[i] + 1:
                self.token.LN[i] = self.RN[i]
                self.token.queue.append(i)

        if self.token.queue:
            newOwner = self.token.queue.popleft()
            print("id = {0} send token via tokenTransfer to: {1}\n".format(self.ident, newOwner))
            self.comm.send(self.token, dest = newOwner, tag = MsgType.TOKEN.value)
            self.hasToken = False
            self.token = None
    
    def wait(self, condString):

        self.mutex.acquire()
        print("id = {0} is in wait status; cond = {1}..\n".format(self.ident, condString))
        if condString in self.token.condQueue.keys():
            self.token.condQueue[condString].append(self.ident)
        else:
            newQueue = deque([self.ident])
            self.token.condQueue[condString] = newQueue
        
        self.tokenTransfer()
        self.inCS = False

        info = MPI.Status()
        self.mutex.release()
        
        tempToken = self.comm.recv(source = MPI.ANY_SOURCE, tag = MsgType.TOKEN.value, status = info)

        self.mutex.acquire()
        self.token = tempToken
        self.hasToken = True
        self.inCS = True
        print("id = {0} wait ended; cond = {1}; token came from {2}..\n".format(self.ident, condString, info.source))
        self.mutex.release()

    def signal(self, condString):
        self.mutex.acquire()
        if condString in self.token.condQueue.keys():     
            if self.token.condQueue[condString]:
                self.token.queue.append(self.token.condQueue[condString].popleft())
        self.mutex.release()

    def signalAll(self, condString):
        self.mutex.acquire()
        if condString in self.token.condQueue.keys():     
            while self.token.condQueue[condString]:
                self.token.queue.append(self.token.condQueue[condString].popleft())
        self.mutex.release()
    
    def getNumerOfElementsOnStack(self):
        if not(self.hasToken): print("You should not be here")
        return self.token.inStock
    
    def putElementOnStack(self):
        if not(self.hasToken): print("You should not be here")
        self.token.inStock+=1


    def popElementFromStack(self):
        if not(self.hasToken): print("You should not be here")
        self.token.inStock-=1

    def recieverThread(self):
        print("id = {0} reciver process started\n".format(self.ident))
        print("id = {0} waiting for a message\n".format(self.ident))
        deadCount = 0
        while True:
            info = MPI.Status()
            self.comm.iprobe(source = MPI.ANY_SOURCE, tag = MPI.ANY_TAG, status = info)
            self.mutex.acquire()
            # self.mutex_lock
            if info.tag == MsgType.REQUEST.value: 
                
                req = self.comm.irecv(source = MPI.ANY_SOURCE, tag = MsgType.REQUEST.value).wait()
                print("id = {0} new request from: {1} with seq = {2}\n".format(self.ident, req.ident,req.seqNo))
                
                # self.RN[req.ident] = req.seqNo if self.RN[req.ident] < req.seqNo else self.RN[req.ident]
                
                if self.RN[req.ident] >= req.seqNo:
                    continue
                
                self.RN[req.ident] = req.seqNo

                if self.hasToken and not(self.inCS) and self.RN[req.ident] == self.token.LN[req.ident] + 1:
                    print("id = {0} send token via thread to: {1}\n".format(self.ident, req.ident))
                    
                    self.token.LN = self.RN
                    self.comm.send(self.token, dest = req.ident, tag = MsgType.TOKEN.value)
                    self.hasToken = False
                    self.token = None
            if info.tag == MsgType.KILL.value:
                req = self.comm.irecv(source = MPI.ANY_SOURCE, tag = MsgType.KILL.value).wait()
                print("id = {0} recieved information about kill from: {1}\n".format(self.ident, req.ident))
                deadCount+=1
                # self.actives.remove(req.ident)
            self.mutex.release()
            if (self.threadLive == False and self.hasToken == False) or (self.comm.Get_size() - deadCount == 1):
                print("id = {0} breaks\n".format(self.ident))
                break
                