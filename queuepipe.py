from queue import Queue
import time
import threading


END=None


def main():
    input, output = make_pipeline([
        print_and_forward,
        Pipeable(lambda x: do_io_bound_stuff(x, 1), parallelism=2),
    ])
    input.put('hello')
    input.put('i')
    input.put('like')
    input.put('cheese')
    input.put('and')
    input.put('wine')
    input.put(END)


def print_and_forward(message: str) -> str:
    print(f'print_and_forward: {message}')
    print(message)
    return message


def do_io_bound_stuff(message: str, delay: int):
    print(f'do_io_bound_stuff: {message}')
    time.sleep(delay)
    print(f'do_io_bound_stuff: {message}, sleep over')
    return message


def make_pipeline(funcs: list) -> (Queue, Queue):
    first_input = Queue()
    input = first_input
    for func in funcs:
        output = Queue()
        if not isinstance(func, Pipeable):
            func = Pipeable(func)
        func.input = input
        func.output = output
        func.start()
        input = output
    return first_input, output


class Pipeable:
    def __init__(self, func, parallelism=1):
        self.func = func
        self.input: Queue = None
        self.output: Queue = None
        self.worker_threads = [threading.Thread(target=self.worker) for _ in range(parallelism)]
        self.cleanup_thread = threading.Thread(target=self.cleanup)

    def worker(self):
        while True:
            item = self.input.get()
            if item is END:
                # ensure that all threads see the END
                self.input.put(END)
                break
            result = self.func(item)
            self.output.put(result)

    def cleanup(self):
        for thread in self.worker_threads:
            thread.join()
        self.output.put(END)

    def start(self):
        for thread in self.worker_threads:
            thread.start()
        self.cleanup_thread.start()



if __name__ == '__main__':
    main()
