from mpi4py import MPI
from Token import Token
from Monitor import Monitor
from Client import Client
from Producer import Producer
from Monitor import Request
from collections import deque
import time
import random


if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    time.sleep(1)

    if rank % 2 == 0:
        prod = Producer()
        for _ in range(6):
            prod.produce(1)
        prod.kill()
    else:
        cli = Client()
        for _ in range(6):
            cli.consume()
        cli.kill()
            
    print("loop ended\n")