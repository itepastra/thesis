from dataclasses import dataclass
from random import Random
from typing import Callable

from tqdm import tqdm

from quantum_circuit import ParametrizedQuantumCircuit


@dataclass
class QualityDiversitySettings:
    """
    Hyperparameters for Quality Diversity based Quantum Architecture Search
    """

    qubits: int

    depth: int

    cost_function: Callable[[list[ParametrizedQuantumCircuit]], list[float]]
    """A function that takes a list of PQC's and returnes the cost of each"""

    sample_function: Callable[[Random], ParametrizedQuantumCircuit]
    """A function that returns a random PQC"""

    initial_population_size: int
    """How many (random) circuits should be generated at the beginning"""

    offspring_size: int
    """How many offspring should be generated from the previous generation"""

    generation_size: int
    """How many of the previous generation offspring become a parent for the next generation"""

    generation_count: int
    """How many generations to optimize for"""

    mutation_rate: float
    """for each gate in a circuit from the offspring perform a mutation if random [0, 1) < mutation_rate"""


def qd_qas(settings: QualityDiversitySettings, random: Random) -> list[ParametrizedQuantumCircuit]:
    initial_population = [
        settings.sample_function(random) for _ in range(settings.initial_population_size)
    ]

    for generation in tqdm(range(settings.generation_count)):
        offspring = ...

    raise NotImplementedError
