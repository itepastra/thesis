import os
import sys
from collections.abc import Generator
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from typing import Any, Callable, Never

from .stream import Stream, T, U


@Stream.extension()
def map(stream: Stream[T], fn: Callable[[T], U]) -> Stream[U]:
    """
    Applies the function `fn` to every element of the stream
    """

    def gen() -> Generator[U, Any, None]:
        for x in stream:
            yield fn(x)

    return Stream(gen())


@Stream.extension()
def par_map(stream: Stream[T], fn: Callable[[T], U], cores: int = 0) -> Stream[U]:

    def gen() -> Generator[U, Any, None]:
        nprocs = (os.cpu_count() or 2) - 1 if cores <= 0 else cores
        inflight = max(1, nprocs)

        it = iter(stream)

        with ProcessPoolExecutor(max_workers=nprocs) as ex:
            pending = set()

            for _ in range(inflight):
                x = next(it)
                pending.add(ex.submit(fn, x))

            while True:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)

                for fut in done:
                    print(f"yielding: {fut}", file=sys.stderr)
                    yield fut.result()
                    x = next(it)
                    pending.add(ex.submit(fn, x))

    return Stream(gen())


@Stream.extension()
def filter(stream: Stream[T], pred: Callable[[T], bool]) -> Stream[T]:
    """
    Applies the predicate `pred` to every element and only returns elements where the predicate is true
    """

    def gen() -> Generator[T, Any, None]:
        for x in stream:
            if pred(x):
                yield x

    return Stream(gen())


@Stream.extension()
def apply(stream: Stream[T], fn: Callable[[T], None]) -> Stream[T]:
    """
    Apply the function `fn` to every element of the stream in-place
    """

    def gen() -> Generator[T, Any, None]:
        for x in stream:
            fn(x)
            yield x

    return Stream(gen())


@Stream.extension()
def take(stream: Stream[T], n: int) -> Stream[T]:
    """
    Return a stream with at most `n` elements
    """

    def gen() -> Generator[T, Any, None]:
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

    def gen() -> Generator[T, Any, None]:
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

    def gen() -> Generator[list[T], Any, None]:
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

    def gen() -> Generator[tuple[int, T], Any, None]:
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
