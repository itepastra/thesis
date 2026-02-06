import random
from collections.abc import Generator
from typing import Never


def sample_hyperspace(
    *args: tuple[int, int] | tuple[float, float], seed: int = 2010392991
) -> Generator[tuple[float | int, ...], None, Never]:
    minimums: tuple[float | int, ...] = tuple(arg[0] for arg in args)
    maximums: tuple[float | int, ...] = tuple(arg[1] for arg in args)
    diffs: tuple[float | int, ...] = tuple(ma - mi for mi, ma in zip(minimums, maximums))
    idiffs: tuple[float, ...] = tuple(1.0 / diff for diff in diffs)
    rng: random.Random = random.Random(seed)

    previous_points: set[tuple[float | int, ...]] = set()

    def dist(point: tuple[float | int, ...], other: tuple[float | int, ...]) -> float:
        return sum(((p - o) * idiff) ** 2 for p, o, idiff in zip(point, other, idiffs))

    while True:
        sampled_points: list[tuple[float | int, ...]] = [
            tuple(
                min
                + (
                    rng.randint(min, min + diff)
                    if isinstance(min, int) and isinstance(diff, int)
                    else rng.uniform(min, min + diff)
                )
                for min, diff in zip(minimums, diffs)
            )
            for _ in range(10)
        ]

        if len(previous_points) == 0:
            previous_points.add(sampled_points[0])
            yield sampled_points[0]

        min_distances: list[float] = [
            min((dist(point, other) for other in previous_points)) for point in sampled_points
        ]

        mdist: float = max(min_distances)
        point: tuple[float | int, ...] = sampled_points[[i for i, j in enumerate(min_distances) if j == mdist][0]]

        previous_points.add(point)
        yield point
