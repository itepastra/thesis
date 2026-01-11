from collections.abc import Iterator
from typing import Any, Callable, Generic, TypeVar, final


T = TypeVar("T")
U = TypeVar("U")

Op = Callable[["Stream[T]"], "Stream[U]"]


@final
class Stream(Generic[T]):
    _extensions: dict[str, Callable[..., Any]] = {}

    def __init__(self, it: Iterator[T]) -> None:
        self._it = it

    def __iter__(self) -> Iterator[T]:
        return self._it

    @classmethod
    def extension(cls, name: str | None = None):
        """Register a function as Stream.<name>(...). First arg will be the stream."""

        def deco(fn: Callable[..., Any]):
            cls._extensions[name or fn.__name__] = fn
            return fn

        return deco

    def __getattr__(self, attr: str):
        fn = self._extensions.get(attr)
        if fn is None:
            raise AttributeError(attr)

        def bound(*args, **kwargs):
            return fn(self, *args, **kwargs)

        return bound
