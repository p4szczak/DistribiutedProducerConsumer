from mpi4py import MPI
from Token import Token
from Monitor import Monitor
from Monitor import Request
from collections import deque
import time
import random


if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    print(rank)
    mon = Monitor()
    # if rank == 0:
    #     pass
        # local = deque([])
        # local.append(1)
        # local.append(10)
        # lista=[1,2,3,4,5,6,7]
        # cond = {"full" : deque([]), "empty" : deque([])}
        # q1 = [1,2,3]
        # cond["full"].append(2)
        # cond["empty"].append(3)
        # cond["asd"] = q1    
        # t1 = Token(lista, local, 2, cond)
        # comm.send(t1, dest=1, tag=2)
        # print(t1)
    # else:
    #     mon.enterCS()
        
    # while(1):
    # for i in range(2): 
        # time.sleep(random.randint(0,3))
    # mon.enterCS()
    while True:
        if rank == 0:
            mon.enterCS()
            mon.exitCS()
            # time.sleep(1)
        else:
            mon.enterCS()
            mon.exitCS()
            # time.sleep(1)
        # while(True): continue
    
    # time.sleep(random.randint(1,10))
    # mon.exitCS()

    # local = deque([])
    # local.append(1)
    # local.append(10)
    # lista=[1,2,3,4,5,6,7]
    # cond = {"full" : deque([]), "empty" : deque([])}
    # q1 = [1,2,3]
    # cond["full"].append(2)
    # cond["empty"].append(3)
    # cond["asd"] = q1
    # if rank == 0:
    #     t1 = Token(lista, local, 2, cond)
    #     comm.send(t1, dest=1, tag=11)
    #     print(t1)
    # else:
    #     t2 = comm.recv(source=0, tag=11)
    #     while t2.queue:
    #         print(t2.queue.popleft())
    #     print(t2)
