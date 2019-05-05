from mpi4py import MPI
from Token import Token
from collections import deque
from enum import Enum
import logging
import threading
import time


comm = MPI.COMM_WORLD


# #enum
# class MsgType(Enum):
REQUEST = 1
TOKEN = 2

class Request:
    def __init__(self, ident, seqNo):
        self.ident = ident
        self.seqNo = seqNo


class Monitor:
    def __init__(self):
        self.RN = [0] * comm.Get_size()
        self.hasToken = False
        self.inCS = False
        self.ident = comm.Get_rank()
        self.token = None
        self.mutex = threading.Lock()
        self.threadLive = True
        if(self.ident == 0):
            print("id = {0} initializing token\n".format(self.ident))
            self.token = Token([0] * comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True
        self.t1 = threading.Thread(target= self.recieverThread)
        self.t1.start()
        # t1.join()

        
    def enterCS(self):
        self.mutex.acquire()
        print("id = {0} trying to enter to CS\n".format(self.ident))
        if(not(self.hasToken)):
            self.sendRequest()
            info = MPI.Status()
            self.mutex.release()
            print("id = {0} is waiting for token\n".format(self.ident))
            tempToken = comm.recv(source = MPI.ANY_SOURCE, tag = TOKEN, status = info)
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
        for i in range(comm.Get_size()):
            # print(type(i))
            
            print("id = {0} sending request to {1}\n".format(self.ident, i))
            if(self.ident == i): continue
            comm.isend(req, dest=i, tag=REQUEST)
    
    def exitCS(self):
        # self.mutex_lock
        self.mutex.acquire()
        print("id = {0} exit CS\n".format(self.ident))
        
        self.tokenRelease()
        print("id = {0} RN: {1}\n".format(self.ident, self.RN))
        self.inCS = False
        # self.mutex_unlock
        self.mutex.release()
        

    def tokenRelease(self):
        for i in range(comm.Get_size()):
            if self.RN[i] == self.token.LN[i] + 1:
                self.token.LN[i] = self.RN[i]
                self.token.queue.append(i)

        if self.token.queue:
            newOwner = self.token.queue.popleft()
            print("id = {0} send token tokenRelease to: {1}\n".format(self.ident, newOwner))
            comm.send(self.token, dest = newOwner, tag = TOKEN)
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
        
        self.tokenRelease()
        self.inCS = False

        info = MPI.Status()
        self.mutex.release()
        
        tempToken = comm.recv(source = MPI.ANY_SOURCE, tag = TOKEN, status = info)

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

    def recieverThread(self):
        print("id = {0} reciver process started\n".format(self.ident))
        print("id = {0} waiting for a message\n".format(self.ident))
        
        while self.threadLive:
            info = MPI.Status()
            
            comm.iprobe(source = MPI.ANY_SOURCE, tag = MPI.ANY_TAG, status = info)
            
            # self.mutex_lock
            
            
            if info.tag == REQUEST: 
                self.mutex.acquire()
                req = comm.irecv(source = MPI.ANY_SOURCE, tag = REQUEST).wait()
                print("id = {0} new request from: {1}\n".format(self.ident, req.ident))
                
                self.RN[req.ident] = req.seqNo if self.RN[req.ident] < req.seqNo else self.RN[req.ident]
                
                if self.hasToken and not(self.inCS) and self.RN[req.ident] == self.token.LN[req.ident] + 1:
                    print("id = {0} send token via thread to: {1}\n".format(self.ident, req.ident))
                    
                    self.token.LN = self.RN
                    comm.send(self.token, dest = req.ident, tag = TOKEN)
                    self.hasToken = False
                    self.token = None
                    
                self.mutex.release()