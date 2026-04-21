#!/usr/bin/env python
import json
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from random import Random

from tqdm import tqdm

import ga_qas
import sampling
import tf_qas
from ga_qas import GeneticAlgorithmSettings
from quantum_circuit import ParametrizedQuantumCircuit, QuantumType
from quantum_circuit.proxies.expressivity import calculate_expressivity
from quantum_circuit.proxies.path import paths_proxy
from quantum_circuit.proxy_config import ProxyConfig
from tf_qas import TrainingFreeSettings


class SearchStrategy(Enum):
    TFQAS = 1
    GAQAS = 2
    QDQAS = 3


def main(search_settings: TrainingFreeSettings | GeneticAlgorithmSettings):

    random = Random()
    qubits = 0
    qas_type = "unknown"
    qas_additional = ""

    result = []
    if isinstance(search_settings, TrainingFreeSettings):
        qubits = search_settings.qubits
        result = tf_qas.tf_qas(search_settings, random)
        qas_type = "training-free"
        qas_additional = search_settings.additional
    elif isinstance(search_settings, GeneticAlgorithmSettings):
        qubits = search_settings.qubits

        history, result = ga_qas.ga_qas(search_settings, random)
        qas_type = "genetic-algorithm"
        qas_additional = search_settings.additional

    found_circuits: list[ParametrizedQuantumCircuit] = []
    for circ, cost in result:
        logging.debug(f"{circ}\ncost: {cost}")
        found_circuits.append(circ)

    # export the resulting circuits to json for the evaluator
    with open(f"{qas_type}-{qubits}-{qas_additional}.json", "w+") as f:
        json.dump(
            [
                {
                    "qubits": circ.qubits,
                    "gates": [
                        {"type": gate.type.value, "qubits": gate.qubits} for layer in circ.gates for gate in layer
                    ],
                }
                for circ in found_circuits
            ],
            f,
        )
        pass


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--strategy", type=str, default="qd", help="Search strategy", choices=["ga", "qd", "tf"])
    parser.add_argument("--qubits", type=int, default=4, help="How many qubits to search a PQC for")
    parser.add_argument("--depth", type=int, default=12, help="How many qubits to search a PQC for")
    parser.add_argument("--extra", type=str, default="", help="Note about the settings for filename")
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

            initial_samples = 50000
            t2_samples = 5000

            search_settings = TrainingFreeSettings(
                args.qubits,
                args.depth,
                cheap_proxy,
                expensive_proxy,
                layer_sampling,
                initial_samples,
                t2_samples,
                f"ours-{initial_samples}-{t2_samples}{"-" if args.extra else ""}{args.extra}",
            )

        case SearchStrategy.GAQAS:

            def expressibility_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
                return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

            search_settings = GeneticAlgorithmSettings(
                args.qubits,
                args.depth,
                expressibility_proxy_value,
                gate_sampling,
                20,
                20,
                13,
                0.1,
                20,
                gate_set,
                f"ours{"-" if args.extra else ""}{args.extra}",
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
                f"diversity{"-" if args.extra else ""}{args.extra}",
            )

    main(search_settings)
