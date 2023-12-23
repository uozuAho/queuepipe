from queue import Queue
from threading import Thread
import time
import pipe


@pipe.Pipe
def print_wait(input, id):
    for x in input:
        print(f'{id}: waiting {x}...')
        time.sleep(x)
        print(f'{id}: waited {x}')
        yield x


class PipeableParallel:
    """argh this is too confusing"""
    def __init__(self, func, parallelism):
        self.func = func
        self.parallelism = parallelism
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.no_more_work = "i am done"

    def __ror__(self, other):
        def worker():
            while True:
                x = self.in_queue.get()
                if x is self.no_more_work:
                    self.out_queue.put(self.no_more_work)
                    return
                self.out_queue.put(self.func(x))

        threads = [Thread(target=worker) for _ in range(self.parallelism)]

        for x in other: self.in_queue.put(x)
        for t in threads: t.start()
        for t in threads: t.join()

    def __next__(self):
        x = self.out_queue.get()
        if x is self.no_more_work:
            raise StopIteration


def parallel_print_wait(input, parallelism=2):
    in_queue = Queue()
    out_queue = Queue()
    no_more_work = "i am done"

    def worker():
        while True:
            x = in_queue.get()
            if x is no_more_work:
                out_queue.put(no_more_work)
                return
            print(f'waiting {x}...')
            time.sleep(x)
            print(f'waited {x}')
            out_queue.put(x)

    def outputter():
        while True:
            x = out_queue.get()
            if x is no_more_work:
                return
            yield x

    threads = [Thread(target=worker) for _ in range(parallelism)]
    threads.append(Thread(target=outputter))

    for x in input: in_queue.put(x)
    for t in threads: t.start()
    for t in threads: t.join()


for x in [1, 2, 1] | print_wait("me1") | print_wait("me2"):
    pass
