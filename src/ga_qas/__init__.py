from dataclasses import dataclass

from settings import QuantumArchitectureSearchSettings


@dataclass
class QualityDiversitySettings(QuantumArchitectureSearchSettings):
    initial_population_size: int
