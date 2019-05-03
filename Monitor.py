from mpi4py import MPI
from Token import Token
from collections import deque
from enum import Enum
import logging
import threading
import time


comm = MPI.COMM_WORLD
mutex = threading.Lock()

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
        if(self.ident == 0):
            print("id = {0} initializing token".format(self.ident))
            self.token = Token([0] * comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True
        t1 = threading.Thread(target= self.recieverThread)
        t1.start()
        # t1.join()

    def enterCS(self):
        mutex.acquire()
        print("id = {0} trying to enter to CS".format(self.ident))
        if(not(self.hasToken)):
            self.sendRequest()
            info = MPI.Status()
            print("id = {0} is waiting for token".format(self.ident))
            self.token = comm.recv(source = MPI.ANY_SOURCE, tag = TOKEN, status = info)
            self.hasToken = True
        print("id = {0} is in CS".format(self.ident))
        self.inCS = True

        mutex.release()

    def sendRequest(self):
        self.RN[self.ident] += 1
        req = Request(self.ident, self.RN[self.ident])
        for i in range(comm.Get_size()):
            print(type(i))
            
            print("id = {0} sending request to {1}".format(self.ident, i))
            if(self.ident == i): continue
            comm.send(obj = req, dest=i, tag=REQUEST)
    
    def exitCS(self):
        # mutex_lock
        mutex.acquire()
        print("id = {0} exit CS".format(self.ident))
        self.tokenRelease()
        
        self.inCS = False
        # mutex_unlock
        mutex.release()

    def tokenRelease(self):
        for i in range(comm.Get_size()):
            if self.RN[i] == self.token.LN[i] + 1:
                self.token.LN[i] = self.RN[i]
                self.token.queue.append(i)

        if self.token.queue:
            newOwner = self.token.queue.popleft()
            comm.send(obj = self.token, dest = newOwner, tag = TOKEN)
            self.hasToken = False
            self.token = None

    def recieverThread(self):
        print("id = {0} reciver process started".format(self.ident))
        print("id = {0} waiting for a message".format(self.ident))
        
        while True:
            info = MPI.Status()
            
            comm.probe(source = MPI.ANY_SOURCE, tag = MPI.ANY_TAG, status = info)
            # mutex_lock
            mutex.acquire()
            if info.tag == REQUEST:
                
                req = comm.recv(source = MPI.ANY_SOURCE, tag = REQUEST)
                print("id = {0} new request from: {1}".format(self.ident, req.ident))
                self.RN[req.ident] = req.seqNo if self.RN[req.ident] < req.seqNo else self.RN[req.ident]
            
                if self.hasToken and not(self.inCS):
                    comm.send(obj = self.token, dest = req.ident, tag = TOKEN)
                    self.hasToken = False
                    self.token = None

            # mutex_unlock
            mutex.release()
