#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from random import Random

from tqdm import tqdm

import ga_qas
import sampling
from ga_qas import GeneticAlgorithmSettings
from qd_qas import QualityDiversitySettings
from quantum_circuit import ParametrizedQuantumCircuit, QuantumType
from quantum_circuit.proxies.expressivity import calculate_expressivity
from quantum_circuit.proxy_config import ProxyConfig
from tf_qas import TrainingFreeSettings


class SearchStrategy(Enum):
    TFQAS = 1
    GAQAS = 2
    QDQAS = 3


def main(
    search_settings: QualityDiversitySettings | TrainingFreeSettings | GeneticAlgorithmSettings,
):

    found_circuits: list[ParametrizedQuantumCircuit] = []

    if isinstance(search_settings, QualityDiversitySettings):
        pass
    elif isinstance(search_settings, TrainingFreeSettings):
        pass
    elif isinstance(search_settings, GeneticAlgorithmSettings):

        history, result = ga_qas.ga_qas(search_settings, Random())

        for circ, cost in result:
            print(f"{circ}\ncost: {cost}")
            found_circuits.append(circ)

    # for each problem type, try the circuits, and then when they succeed the problem log it and continue to the next


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--strategy", type=str, default="qd", help="Search strategy", choices=["ga", "qd", "tf"]
    )
    parser.add_argument("--qubits", type=int, default=4, help="How many qubits to search a PQC for")
    parser.add_argument("--depth", type=int, default=12, help="How many qubits to search a PQC for")
    args = parser.parse_args()

    strat = {"ga": SearchStrategy.GAQAS, "qd": SearchStrategy.QDQAS, "tf": SearchStrategy.TFQAS}[
        args.strategy
    ]
    proxy_config = ProxyConfig(args.qubits)

    gate_set = [
        QuantumType.Hadamard,
        QuantumType.RX,
        QuantumType.RY,
        QuantumType.RZ,
        QuantumType.CX,
    ]

    def sampling_func(random: Random):
        return sampling.sample_by_gates(args.qubits, args.depth, gate_set, random)

    match strat:
        case SearchStrategy.TFQAS:
            pass
        case SearchStrategy.GAQAS:

            def expressibility_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

            search_settings = GeneticAlgorithmSettings(
                args.qubits,
                args.depth,
                expressibility_proxy_value,
                sampling_func,
                20,
                20,
                15,
                0.3,
                20,
                gate_set,
            )
        case SearchStrategy.QDQAS:

            def expressibility_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return list(calculate_expressivity(circs, proxy_config))

            search_settings = QualityDiversitySettings(
                args.qubits,
                args.depth,
                expressibility_proxy_value,
                sampling_func,
                20,
                20,
                20,
                20,
                0.01,
            )

    main(search_settings)
