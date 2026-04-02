from collections.abc import Callable
from dataclasses import dataclass
from itertools import repeat
from operator import itemgetter
from random import Random

import qas_flow
from qas_flow import Stream
from quantum_circuit import ParametrizedQuantumCircuit


@dataclass
class TrainingFreeSettings:
    qubits: int

    depth: int

    cheap_cost_function: Callable[[list[ParametrizedQuantumCircuit]], list[float]]
    """A function that takes a list of PQC's and returnes the cost of each, 
    should be fast as it will run on each of the samples (`sample_size`)"""

    expensive_cost_function: Callable[[list[ParametrizedQuantumCircuit]], list[float]]
    """A function that takes a list of PQC's and returnes the cost of each, 
    can be slower, as it will only run on the samples that pass the first filter (`post_cheap_cost_function`)"""

    sample_function: Callable[[Random], ParametrizedQuantumCircuit]
    """A function that returns a random PQC"""

    sample_size: int
    """How many random circuits to sample from the `sample_function`"""

    post_fast_cost_function_size: int
    """How many circuits should be allowed past the `cheap_cost_function` filter"""


def tf_qas(settings: TrainingFreeSettings, random: Random) -> list[ParametrizedQuantumCircuit]:
    samples = [settings.sample_function(random) for _ in range(settings.sample_size)]

    fast_cost_estimate = settings.cheap_cost_function(samples)

    sorted_fast_cost: list[tuple[ParametrizedQuantumCircuit, int | float]] = sorted(
        zip(samples, fast_cost_estimate), key=itemgetter(1)
    )

    post_fast_cost_circuits = [
        x for x, _ in sorted_fast_cost[: settings.post_fast_cost_function_size]
    ]

    slow_cost_estimate = settings.expensive_cost_function(post_fast_cost_circuits)

    sorted_slow_cost: list[tuple[ParametrizedQuantumCircuit, int | float]] = sorted(
        zip(post_fast_cost_circuits, slow_cost_estimate), key=itemgetter(1)
    )

    return [x for x, _ in sorted_slow_cost]
