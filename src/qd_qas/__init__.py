from dataclasses import dataclass
from typing import Callable

from settings import QuantumArchitectureSearchSettings


@dataclass
class QualityDiversitySettings(QuantumArchitectureSearchSettings):
    """
    Hyperparameters for Quality Diversity based Quantum Architecture Search
    """

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

    cost_function: Callable[[ParametrizedQuantumCircuit], float]
