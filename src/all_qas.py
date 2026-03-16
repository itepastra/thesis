#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum

from ga_qas import GeneticAlgorithmSettings
from qd_qas import QualityDiversitySettings
from settings import QuantumArchitectureSearchSettings
from tf_qas import TrainingFreeSettings


class SearchStrategy(Enum):
    TFQAS = 1
    GAQAS = 2
    QDQAS = 3


def main(search_settings: QualityDiversitySettings | TrainingFreeSettings | GeneticAlgorithmSettings):
    pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--strategy", type=SearchStrategy, default=SearchStrategy.QDQAS, help="Search strategy")
    args = parser.parse_args()
    main(args.strategy)
