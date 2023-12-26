from queue import Queue
import threading


END=None


def make_pipeline(*funcs) -> (Queue, Queue):
    first_input = Queue()
    input = first_input
    for func in funcs:
        output = Queue()
        if not isinstance(func, Apply):
            func = Apply(func)
        func.input = input
        func.output = output
        func.start()
        input = output
    return first_input, output


class Apply:
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
            try:
                result = self.func(item)
                self.output.put(result)
            except Exception as e:
                print(f'Exception "{e}", dropping input "{item}"')

    def cleanup(self):
        for thread in self.worker_threads:
            thread.join()
        self.output.put(END)

    def start(self):
        for thread in self.worker_threads:
            thread.start()
        self.cleanup_thread.start()


class Collect(Apply):
    """ Saves all inputs and sends them all to the output when END is received
    """
    def __init__(self):
        super().__init__(None, 1)

    def worker(self):
        items = []
        while True:
            item = self.input.get()
            if item is END:
                self.output.put(items)
                break
            else:
                items.append(item)
