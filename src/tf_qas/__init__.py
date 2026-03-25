from collections.abc import Callable
from dataclasses import dataclass
from random import Random

from quantum_circuit import ParametrizedQuantumCircuit


@dataclass
class TrainingFreeSettings:
    qubits: int

    depth: int

    cost_function: Callable[[list[ParametrizedQuantumCircuit]], list[float]]
    """A function that takes a list of PQC's and returnes the cost of each"""

    sample_function: Callable[[Random], ParametrizedQuantumCircuit]
    """A function that returns a random PQC"""
    sample_size: int
