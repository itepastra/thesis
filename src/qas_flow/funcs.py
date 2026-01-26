from typing import Callable
from .stream import Stream, T, U


@Stream.extension()
def map(stream: Stream[T], fn: Callable[[T], U]) -> Stream[U]:
    """
    Applies the function `fn` to every element of the stream
    """

    def gen():
        for x in stream:
            yield fn(x)

    return Stream(gen())


@Stream.extension()
def filter(stream: Stream[T], pred: Callable[[T], bool]) -> Stream[T]:
    """
    Applies the predicate `pred` to every element and only returns elements where the predicate is true
    """

    def gen():
        for x in stream:
            if pred(x):
                yield x

    return Stream(gen())


@Stream.extension()
def apply(stream: Stream[T], fn: Callable[[T], None]) -> Stream[T]:
    """
    Apply the function `fn` to every element of the stream in-place
    """

    def gen():
        for x in stream:
            fn(x)
            yield x

    return Stream(gen())


@Stream.extension()
def take(stream: Stream[T], n: int) -> Stream[T]:
    """
    Return a stream with at most `n` elements
    """

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
    """
    Ignore the first `n` elements of a stream
    """

    def gen():
        c = 0
        for x in stream:
            c += 1
            if c > n:
                yield x

    return Stream(gen())


@Stream.extension()
def batch(stream: Stream[T], n: int) -> Stream[list[T]]:
    """
    Create batches of size `n` from the stream
    """

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
    """
    Add an index to each element of the stream
    """

    def gen():
        idx = 0
        for x in stream:
            yield (idx, x)
            idx += 1

    return Stream(gen())


@Stream.extension()
def collect(stream: Stream[T]) -> list[T]:
    """
    Create a list from the elements of the stream greedily
    """
    return [v for v in stream]
