#!/usr/bin/env python
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from random import Random

import tensorcircuit as tc
from tqdm import tqdm

import ga_qas
import sampling
import tf_qas
from ga_qas import GeneticAlgorithmSettings
from problems import benchmark_qas
from problems.tfim import make_problem_function
from quantum_circuit import ParametrizedQuantumCircuit, QuantumType
from quantum_circuit.proxies.expressivity import calculate_expressivity
from quantum_circuit.proxies.path import paths_proxy
from quantum_circuit.proxy_config import ProxyConfig
from tf_qas import TrainingFreeSettings

tc.set_backend("tensorflow")
tc.set_dtype("complex128")


class SearchStrategy(Enum):
    TFQAS = 1
    GAQAS = 2
    QDQAS = 3


def main(search_settings: TrainingFreeSettings | GeneticAlgorithmSettings):

    random = Random()
    qubits = 0

    result = []
    if isinstance(search_settings, TrainingFreeSettings):
        qubits = search_settings.qubits
        result = tf_qas.tf_qas(search_settings, random)
    elif isinstance(search_settings, GeneticAlgorithmSettings):
        qubits = search_settings.qubits

        history, result = ga_qas.ga_qas(search_settings, random)

    found_circuits: list[ParametrizedQuantumCircuit] = []
    for circ, cost in result:
        logging.debug(f"{circ}\ncost: {cost}")
        found_circuits.append(circ)

    # for each problem type, try the circuits, and then when they succeed the problem log it and continue to the next

    benchmark_qas(found_circuits, make_problem_function(qubits, True, 0.01, random.randrange(10000, 1000000)), True)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--strategy", type=str, default="qd", help="Search strategy", choices=["ga", "qd", "tf"])
    parser.add_argument("--qubits", type=int, default=4, help="How many qubits to search a PQC for")
    parser.add_argument("--depth", type=int, default=12, help="How many qubits to search a PQC for")
    args = parser.parse_args()

    strat = {"ga": SearchStrategy.GAQAS, "qd": SearchStrategy.QDQAS, "tf": SearchStrategy.TFQAS}[args.strategy]
    proxy_config = ProxyConfig(args.qubits)

    gate_set = [QuantumType.Hadamard, QuantumType.RX, QuantumType.RY, QuantumType.RZ, QuantumType.CX]

    def gate_sampling(random: Random):
        return sampling.sample_by_gates(args.qubits, args.depth, gate_set, random)

    def layer_sampling(random: Random):
        return sampling.sample_by_layers(args.qubits, args.depth, gate_set, random, True)

    match strat:
        case SearchStrategy.TFQAS:

            def cheap_proxy(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return [float(x) for x in paths_proxy(circs)]

            def expensive_proxy(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

            search_settings = TrainingFreeSettings(
                args.qubits, args.depth, cheap_proxy, expensive_proxy, layer_sampling, 50000, 5000
            )

        case SearchStrategy.GAQAS:

            def expressibility_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

            search_settings = GeneticAlgorithmSettings(
                args.qubits, args.depth, expressibility_proxy_value, gate_sampling, 20, 20, 15, 0.3, 4, gate_set
            )
        case SearchStrategy.QDQAS:

            def expressibility_distance_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                target_expressibility = -0.05
                return [abs(-float(x) - target_expressibility) for x in calculate_expressivity(circs, proxy_config)]

            search_settings = GeneticAlgorithmSettings(
                args.qubits,
                args.depth,
                expressibility_distance_proxy_value,
                gate_sampling,
                20,
                20,
                15,
                0.3,
                20,
                gate_set,
            )

    main(search_settings)
