from collections import deque
try:
    import queue
except ImportError:
    import Queue as queue

class Token:
    def __init__(self, LN, queue, inStock, condQueue):
        self.LN = LN
        self.inStock = inStock
        self.queue = queue
        self.condQueue = condQueue
        
    def __repr__(self):
        return "{0} {1} {2} {3}".format(self.LN, self.queue, self.inStock, self.condQueue)
    def __str__(self):
        return "{0} {1} {2} {3}".format(self.LN, self.queue, self.inStock, self.condQueue)

