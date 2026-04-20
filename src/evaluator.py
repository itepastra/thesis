#!/usr/bin/env python
import json
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from py import path
from tqdm import tqdm

from evaluator.problems import benchmark_qas
from evaluator.problems.tfim import make_problem_function as make_tfim_problem
from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType
from quantum_circuit.proxy_config import ProxyConfig

BASICS = "basics"
EXPRESSIVITY = "expressivity"
PATHS = "paths"
TFIM = "tfim"
TFIM_NON_PERIOD = "tfim_non_period"


def parse_circuit(circuit) -> ParametrizedQuantumCircuit:
    c = ParametrizedQuantumCircuit(circuit["qubits"])

    gates = [QuantumGate(QuantumType(gate["type"]), tuple(gate["qubits"])) for gate in circuit["gates"]]

    for gate in gates:
        c.append_gate(gate)
    c.check_parameters(False)

    return c


def expressivity(file: Path, circuits: list[ParametrizedQuantumCircuit]):
    print(f"calculating expressivities")
    with open(file, "w+") as f:
        f.write("index,expressivity\n")
        for i, circ in tqdm(enumerate(circuits), total=len(circuits), leave=False):
            f.write(f"{i},{circ.expressivity(ProxyConfig(circ.qubits))}\n")


def paths(file: Path, circuits: list[ParametrizedQuantumCircuit]):
    from quantum_circuit.proxies.path import count_paths, make_dag

    print(f"calculating paths")

    def calc_paths(circ: ParametrizedQuantumCircuit) -> int:
        dag = make_dag(circ)
        node_count = len(dag)
        return count_paths(dag, 0, node_count - 1, [None for _ in range(node_count)])

    with open(file, "w+") as f:
        f.write("index,paths\n")
        for i, circ in tqdm(enumerate(circuits), total=len(circuits), leave=False):
            f.write(f"{i},{calc_paths(circ)}\n")


def tfim(file: Path, circuits: list[ParametrizedQuantumCircuit], periodic: bool):
    print(f"calculating {"periodic" if periodic else "non-periodic"} tfim energies")
    with open(file, "w+") as f:
        pfunc, true_energy = make_tfim_problem(circuits[0].qubits, periodic)
        benchmark_qas(circuits, pfunc, f, true_energy, True)


def basics(file: Path, circuits: list[ParametrizedQuantumCircuit]):
    print(f"calculating basic circuit stats")
    with open(file, "w+") as f:
        f.write(f"index,depth,gates,parameters\n")
        for i, circ in tqdm(enumerate(circuits), total=len(circuits), leave=False):
            f.write(f"{i},{len(circ.gates)},{sum(len(layer) for layer in circ.gates)},{circ.parameters}\n")


def main(file: Path, seed: int | None, savepath: Path, skip_existing: bool, parts_to_do: set[str]):
    print("loading file")
    with open(file, "r") as f:
        circuits = json.load(f)

    print("parsing circuits")
    parsed_circuits: list[ParametrizedQuantumCircuit] = [parse_circuit(circuit) for circuit in circuits]

    print(f"setting up save folder at {savepath}")
    os.makedirs(savepath, exist_ok=True)

    eval_functions = {
        EXPRESSIVITY: lambda f: expressivity(f, parsed_circuits),
        PATHS: lambda f: paths(f, parsed_circuits),
        TFIM: lambda f: tfim(f, parsed_circuits, True),
        TFIM_NON_PERIOD: lambda f: tfim(f, parsed_circuits, False),
        BASICS: lambda f: basics(f, parsed_circuits),
    }

    for part in parts_to_do:
        f = savepath.joinpath(part)
        if skip_existing and f.exists():
            continue
        eval_functions[part](f)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="QAS-Evaluator",
        description="Program that reads a QAS output collection and optimises it against a set of problems",
    )

    parser.add_argument("--seed", type=int, default=None, help="Seed to evaluate with, if given")
    parser.add_argument("--skip_existing", action="store_true")
    parser.add_argument("filename", type=Path, help="Circuit file to load")
    parser.add_argument("savepath", type=Path, help="directory to create and save the results")

    tests = parser.add_argument_group("tests", "Wether to perform certain tests or not")

    test_types = [TFIM, PATHS, EXPRESSIVITY, TFIM_NON_PERIOD, BASICS]
    for arg in test_types:
        tests.add_argument(f"--{arg}", action="store_true")

    args: Namespace = parser.parse_args()

    to_do: set[str] = set()
    for arg in test_types:
        if vars(args)[arg]:
            to_do.add(arg)

    main(args.filename, args.seed, args.savepath, args.skip_existing, to_do)
