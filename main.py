from mpi4py import MPI
from Token import Token
from Monitor import Monitor
from collections import deque



if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    mon = Monitor()
    local = deque([])
    local.append(1)
    local.append(10)
    lista=[1,2,3,4,5,6,7]
    cond = {"full" : deque([]), "empty" : deque([])}
    q1 = [1,2,3]
    cond["full"].append(2)
    cond["empty"].append(3)
    cond["asd"] = q1
    if rank == 0:
        t1 = Token(lista, local, 2, cond)
        comm.send(t1, dest=1, tag=11)
    else:
        t2 = comm.recv(source=0, tag=11)
        while t2.queue:
            print(t2.queue.popleft())
        print(t2)
