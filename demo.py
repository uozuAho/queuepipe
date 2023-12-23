import time
import queuepipe as qp


def main():
    input, output = qp.make_pipeline([
        print_and_forward,
        qp.Pipeable(lambda x: do_io_bound_stuff(x, 1), parallelism=2),
        i_return_many_values,
        i_consume_many_args,
    ])
    input.put('hello')
    input.put('i')
    input.put('like')
    input.put('cheese')
    input.put('and')
    input.put('wine')
    input.put(qp.END)


def print_and_forward(message: str) -> str:
    print(f'print_and_forward: {message}')
    print(message)
    return message


def do_io_bound_stuff(message: str, delay: int):
    print(f'do_io_bound_stuff: {message}')
    time.sleep(delay)
    print(f'do_io_bound_stuff: {message}, sleep over')
    return message


def i_return_many_values(x):
    return x, x, x


def i_consume_many_args(a):
    x, y, z = a
    print(x, y, z)


if __name__ == '__main__':
    main()
