from typing import Callable
from .stream import Stream, T, U


@Stream.extension()
def map(stream: Stream[T], fn: Callable[[T], U]) -> Stream[U]:
    def gen():
        for x in stream:
            yield fn(x)

    return Stream(gen())


@Stream.extension()
def filter(stream: Stream[T], pred: Callable[[T], bool]) -> Stream[T]:
    def gen():
        for x in stream:
            if pred(x):
                yield x

    return Stream(gen())


@Stream.extension()
def take(stream: Stream[T], n: int) -> Stream[T]:
    def gen():
        c = 0
        for x in stream:
            if c < n:
                c += 1
                yield x
            else:
                return

    return Stream(gen())


@Stream.extension()
def skip(stream: Stream[T], n: int) -> Stream[T]:
    def gen():
        c = 0
        for x in stream:
            c += 1
            if c > n:
                yield x

    return Stream(gen())


@Stream.extension()
def batch(stream: Stream[T], n: int) -> Stream[list[T]]:
    def gen():
        ls: list[T] = []
        for x in stream:
            ls.append(x)
            if len(ls) == n:
                yield ls
                ls = []

    return Stream(gen())


@Stream.extension()
def enumerate(stream: Stream[T]) -> Stream[tuple[int, T]]:
    def gen():
        idx = 0
        for x in stream:
            yield (idx, x)
            idx += 1

    return Stream(gen())


@Stream.extension()
def collect(stream: Stream[T]) -> list[T]:
    return [v for v in stream]
