import time
import queuepipe as qp


def main():
    input, output = qp.make_pipeline(
        task_a,
        qp.Pipeable(lambda x: task_b(x, 1), parallelism=3),
        task_c,
        task_d,
        qp.Collect(),
        lambda x: print(f'collected outputs: {x}')
    )
    input.put('hello')
    input.put('i')
    input.put('like')
    input.put('cheese')
    input.put('and')
    input.put('wine')
    input.put(qp.END)


def task_a(message: str) -> str:
    print(f'task_a: {message}')
    return message


def task_b(message: str, delay: int):
    print(f'task_b: {message}')
    time.sleep(delay)
    print(f'task_b: {message}, done')
    return message


def task_c(x):
    return x, x, x


def task_d(a):
    x, y, z = a
    print(f'task d: {x, y, z}')
    return a


if __name__ == '__main__':
    main()
