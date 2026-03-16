from dataclasses import dataclass

from settings import QuantumArchitectureSearchSettings


@dataclass
class TrainingFreeSettings(QuantumArchitectureSearchSettings):
    sample_size: int
