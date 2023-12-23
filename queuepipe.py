from queue import Queue
import time
import threading


END=None


def main():
    input, output = make_pipeline([
        print_and_forward,
        Pipeable(lambda x: do_io_bound_stuff(x, 1))
    ])
    input.put('hello')
    input.put(END)
    while True:
        item = output.get()
        print(f'read {item} from output')
        if item is END:
            break


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
        if isinstance(func, Pipeable):
            func.input = input
            func.output = output
            func.start()
        else:
            makepipeable(func, input, output)
        input = output
    return first_input, output


class Pipeable:
    def __init__(self, func):
        self.func = func
        self.input: Queue = None
        self.output: Queue = None
        self.thread = threading.Thread(target=self.worker)

    def worker(self):
        while True:
            item = self.input.get()
            if item is END:
                self.output.put(END)
                break
            result = self.func(item)
            self.output.put(result)

    def start(self):
        self.thread.start()


def makepipeable(func, input: Queue, output: Queue):
    def worker():
        while True:
            item = input.get()
            if item is END:
                output.put(END)
                break
            result = func(item)
            output.put(result)
    thread = threading.Thread(target=worker)
    thread.start()


if __name__ == '__main__':
    main()
