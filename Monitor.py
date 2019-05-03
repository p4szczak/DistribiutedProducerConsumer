from mpi4py import MPI
from Token import Token
from collections import deque
from enum import Enum
import logging
import threading
import time


comm = MPI.COMM_WORLD


#enum
class MsgType(Enum):
    REQUEST = 1
    TOKEN = 2

class Request:
    def init(self, ident, seqNo):
        self.ident = ident
        self.seqNo = seqNo


class Monitor:
    def init(self):
        self.RN = [0] * comm.Get_size()
        self.hasToken = False
        self.inCS = False
        self.ident = comm.Get_rank()
        self.token = None
        self.mutex = threading.Lock()
        if(comm.Get_rank() == 0):
            self.token = Token([0] * comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True
        t1 = threading.Thread(target= self.recieverThread)
        t1.start()

    def enterCS(self):
        self.mutex.acquire()

        if(not(self.hasToken)):
            self.sendRequest()
            info = MPI.Status()
            comm.recv(buf = self.token, source = MPI.ANY_SOURCE, tag = MsgType.TOKEN, status = info)
            self.hasToken = True

        self.inCS = True

        self.mutex.release()

    def sendRequest(self):
        for i in range(comm.Get_size()):
            self.RN[self.ident] += 1
            req = Request(self.ident, self.RN[self.ident])
            if(self.ident == i): continue
            comm.send(req, dest=i, tag=MsgType.REQUEST)
    
    def exitCS(self):
        # mutex_lock
        self.mutex.acquire()

        self.tokenRelease()
        
        self.inCS = False
        # mutex_unlock
        self.mutex.release()

    def tokenRelease(self):
        for i in range(comm.Get_size()):
            if self.RN[i] == self.token.LN[i] + 1:
                self.token.LN[i] = self.RN[i]
                self.token.queue.append(i)

        if self.token.queue:
            newOwner = self.token.queue.popleft()
            comm.send(obj = self.token, dest = newOwner, tag = MsgType.TOKEN)
            self.hasToken = False
            self.token = None

    def recieverThread(self):
        while True:
            info = MPI.Status()
            comm.probe(source = MPI.ANY_SOURCE, tag = MPI.ANY_TAG, status = info)
            # mutex_lock
            self.mutex.acquire()
            if info.MPI.tag == MsgType.REQUEST:
                req = Request(-1, -1)
                comm.recv(buf = req, source = MPI.ANY_SOURCE, tag = MsgType.REQUEST)
                self.RN[req.ident] = req.seqNo if self.RN[req.ident] < req.seqNo else self.RN[req.ident]
            
            if self.hasToken and not(self.inCS):
                comm.send(obj = self.token, dest = req.ident, tag = MsgType.TOKEN)
                self.hasToken = False
                self.token = None
            # mutex_unlock
            self.mutex.release()
