#!/usr/bin/env python
import json
import os
from argparse import ArgumentParser
from pathlib import Path

import evaluator.problems.tfim as tfim
from evaluator.problems import benchmark_qas
from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


def parse_circuit(circuit) -> ParametrizedQuantumCircuit:
    c = ParametrizedQuantumCircuit(circuit["qubits"])

    gates = [QuantumGate(QuantumType(gate["type"]), tuple(gate["qubits"])) for gate in circuit["gates"]]

    for gate in gates:
        c.append_gate(gate)
    c.check_parameters(False)

    return c


def main(file: Path, seed: int | None, savepath: Path, skip_existing: bool):
    print("loading file")
    with open(file) as f:
        circuits = json.load(f)

    print("parsing circuits")
    parsed_circuits = [parse_circuit(circuit) for circuit in circuits]

    print(f"setting up save folder at {savepath}")
    os.makedirs(savepath, exist_ok=True)

    tfim_file = savepath.joinpath("tfim_periodic_log")
    if not (skip_existing and tfim_file.exists()):
        with open(tfim_file, "w+") as f:
            pfunc, true_energy = tfim.make_problem_function(parsed_circuits[0].qubits, True)
            benchmark_qas(parsed_circuits, pfunc, f, true_energy, True)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="QAS-Evaluator",
        description="Program that reads a QAS output collection and optimises it against a set of problems",
    )

    parser.add_argument("--seed", type=int, default=None, help="Seed to evaluate with, if given")
    parser.add_argument("--skip_existing", action="store_true")
    parser.add_argument("filename", type=Path, help="Circuit file to load")
    parser.add_argument("savepath", type=Path, help="directory to create and save the results")

    args = parser.parse_args()

    main(args.filename, args.seed, args.savepath, args.skip_existing)
