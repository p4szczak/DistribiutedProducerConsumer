from mpi4py import MPI
from Token import Token
from collections import deque
from enum import Enum

comm = MPI.COMM_WORLD


#enum
class MsgType(Enum):
    REQUEST = 1
    TOKEN = 2

class Request:
    def init(self, ident, reqNo):
        self.ident = ident
        self.reqNo = reqNo


class Monitor:
    def init(self):
        self.RN = [0] * comm.Get_size()
        self.hasToken = False
        self.inCS = False
        self.ident = comm.Get_rank()
        self.inSection = False
        self.token = None
        if(comm.Get_rank() == 0):
            self.token = Token([0] * comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True

    def enterCS(self):
        if(not(self.hasToken)):
            self.sendRequest()
            # info = MPI.Status()
            comm.recv(self.token, source=MPI.ANY_SOURCE, tag = MsgType.TOKEN)

    def sendRequest(self):
        for i in range(comm.Get_size()):
            self.RN[self.ident] += 1
            req = Request(self.ident, self.RN[self.ident])
            if(self.ident == i): continue
            comm.send(req, dest=i, tag=MsgType.REQUEST)
