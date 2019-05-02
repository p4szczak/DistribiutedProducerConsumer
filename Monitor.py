from mpi4py import MPI
from Token import Token
from collections import deque

comm = MPI.COMM_WORLD

class Monitor:
    def init(self):
        self.RN = [0] * comm.Get_size()
        self.hasToken = False
        self.inCS = False
        self.id = comm.Get_rank()
        self.inSection = False
        if(comm.Get_rank() == 0):
            token = Token([0] * comm.Get_size(), deque([]) , 0, {})
            self.hasToken = True

    def enterCS(self):
        if(not(hasToken)):
            
    def sendRequest(self):
        pass