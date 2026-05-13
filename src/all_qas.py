#!/usr/bin/env python
import json
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from functools import Placeholder, partial
from random import Random
from typing import Callable

from tqdm import tqdm

import ga_qas
import sampling
import tf_qas
from ga_qas import GeneticAlgorithmSettings
from quantum_circuit import GateType, ParametrizedQuantumCircuit
from quantum_circuit.proxies.expressivity import calculate_expressivity
from quantum_circuit.proxies.path import paths_proxy
from quantum_circuit.proxy_config import ProxyConfig
from sampling import ignore_too_many_two_qubit_gates
from tf_qas import TrainingFreeSettings


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


GA_NAME = "ga"
TF_NAME = "tf"
RAND_NAME = "random"

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("strategy", type=str, help="Search strategy", choices=[GA_NAME, TF_NAME, RAND_NAME])
    parser.add_argument("sampler", type=str, help="Sampling strategy", choices=["layerwise", "gatewise", "gate_filled"])
    parser.add_argument("--qubits", type=int, default=5, help="How many qubits to search a PQC for")
    parser.add_argument("--depth", type=int, default=15, help="How many layers the PQC can have at most")
    parser.add_argument(
        "--params", type=int, default=35, help="How many parameters the PQC can have at most (might be a bit more)"
    )
    parser.add_argument("--extra", type=str, default="", help="Note about the settings for filename")
    args = parser.parse_args()

    proxy_config = ProxyConfig(args.qubits)

    gate_set = [GateType.RX, GateType.RY, GateType.RZ, GateType.RXX, GateType.RYY, GateType.RZZ]

    match args.sampler:
        case "layerwise":

            sampler = partial(
                sampling.sample_by_layers, args.qubits, args.depth, args.params, gate_set, Placeholder, True
            )

        case "gatewise":

            def gate_sampling(random: Random):
                return sampling.sample_by_gates(args.qubits, args.depth, args.params, gate_set, random)

            sampler = gate_sampling

        case "gate_filled":

            def gate_sampling(random: Random):
                return sampling.sample_by_gates_fill(args.qubits, args.depth, args.params, gate_set, random)

            sampler = gate_sampling

    if args.strategy == TF_NAME:

        def cheap_proxy(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
            return [-float(x) for x in paths_proxy(circs)]

        def expensive_proxy(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
            return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

        samples = 50000
        t2_samples = 5000

        search_settings = TrainingFreeSettings(
            args.qubits,
            args.depth,
            cheap_proxy,
            expensive_proxy,
            ignore_too_many_two_qubit_gates(sampler, 0.5),
            samples,
            t2_samples,
            f"ours-{samples}-{t2_samples}{"-" if args.extra else ""}{args.extra}",
        )

    elif args.strategy == GA_NAME:

        def expressibility_proxy_value(circs: list[ParametrizedQuantumCircuit]) -> list[float]:
            return [-float(x) for x in calculate_expressivity(circs, proxy_config)]

        search_settings = GeneticAlgorithmSettings(
            args.qubits,
            args.depth,
            expressibility_proxy_value,
            sampler,
            20,
            20,
            13,
            0.1,
            20,
            gate_set,
            f"ours{"-" if args.extra else ""}{args.extra}",
        )

    elif args.strategy == RAND_NAME:
        samples = 5000

        search_settings = RandomSettings(args.qubits, args.depth, sampler, samples)

    main(search_settings)
