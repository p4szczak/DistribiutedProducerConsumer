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
    print("rank: {0}\n".format(rank))
    mon = Monitor()
    time.sleep(1)



    # print("Poszpalam")
    # if rank == 0:
    #     for i in range(10):
    #         req = Request(0,i)
    #         comm.send(req, dest = 1, tag = 1)
    # # else:
    #     for i in range(10):
    #         req1 = comm.recv(source = MPI.ANY_SOURCE, tag = 1)
    #         print(req1.ident, req1.seqNo)
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

    # # dzialalo nie usuwac
    # for _ in range(5):
    #     if rank == 0:
    #         mon.enterCS()
    #         czas2 = random.randint(1,5)
    #         time.sleep(czas2)
    #         mon.exitCS()
    #         czas = random.randint(1,5)
    #         print("{0} gonna sleep for {1}\n".format(rank,czas))
    #         time.sleep(czas)
    #     else:
    #         mon.enterCS()
    #         czas2 = random.randint(1,5)
    #         time.sleep(czas2)
    #         mon.exitCS()
    #         czas = random.randint(1,5)
    #         print("{0} gonna sleep for {1}\n".format(rank,czas))
    #         time.sleep(czas)
        
    # print("rank: {0} - main thread stop\n".format(rank))

    
    if rank % 2 == 0: #PRODUCENT
        for _ in range(10):
            czas2 = random.randint(1,5)
            time.sleep(czas2)
            mon.enterCS()
            print("before: {0}\n".format(mon.token.inStock))
            while(mon.token.inStock == 1): mon.wait("FULL")
            print("rank: 0 produkuje..\n")
            mon.token.inStock+=1
            print("after: {0}\n".format(mon.token.inStock))
            mon.signalAll("EMPTY")
            mon.exitCS()
    else:
        for _ in range(10):
            czas2 = random.randint(1,5)
            time.sleep(czas2)
            mon.enterCS()
            print("before: {0}\n".format(mon.token.inStock))
            while(mon.token.inStock == 0): mon.wait("EMPTY")
            print("rank: 1 konsumuje..\n")
            mon.token.inStock-=1
            print("after: {0}\n".format(mon.token.inStock))
            mon.signalAll("FULL")
            mon.exitCS()
    print("loop ended\n")
    mon.threadLive = False

    
        
    # neq = deque([])
    # neq.append(1)
    # print(neq)