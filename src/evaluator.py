#!/usr/bin/env python
import glob
import json
import os
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from functools import reduce
from os.path import basename
from pathlib import Path

import pandas as pd
from py import path
from tqdm import tqdm

from evaluator.problems import benchmark_qas
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
    from evaluator.problems.tfim import make_problem_function as make_tfim_problem

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


def create_merged(savepath: Path):
    output_name = "merged.csv"
    index_name = "index"

    csv_files: list[str] = [f for f in glob.glob(str(savepath.joinpath("*.csv"))) if basename(f) != output_name]

    column_counts: dict[str, int] = {}

    for file in tqdm(csv_files, leave=False, desc="reading csv headers"):
        df: pd.DataFrame = pd.read_csv(file, nrows=0, comment="#")
        for col in df.columns:
            if col != index_name:
                column_counts[col] = column_counts.get(col, 0) + 1

    dfs: list[pd.DataFrame] = []

    for file in tqdm(csv_files, leave=False, desc="reading csv files"):
        df = pd.read_csv(file, comment="#")

        if index_name not in df.columns:
            raise ValueError(f"'{index_name}' column not found in {file}")

        file_name: str = os.path.splitext(os.path.basename(file))[0]

        rename_map: dict[str, str] = {}
        for col in df.columns:
            if col != index_name and column_counts[col] > 1:
                rename_map[col] = f"{file_name}_{col}"

        df: pd.DataFrame = df.rename(columns=rename_map)
        dfs.append(df)

    merged: pd.DataFrame = reduce(lambda left, right: pd.merge(left, right, on=index_name), dfs)
    cols = merged.columns.tolist()

    sorted_cols = ["index"] + sorted([c for c in cols if c != "index"])
    merged = merged[sorted_cols]

    merged.to_csv(savepath.joinpath(output_name), index=False)


def evaluate(
    circuits: list[ParametrizedQuantumCircuit],
    seed: int | None,
    savepath: Path,
    skip_existing: bool,
    parts_to_do: set[str],
):

    print(f"setting up save folder at {savepath}")
    os.makedirs(savepath, exist_ok=True)

    eval_functions = {
        EXPRESSIVITY: lambda f: expressivity(f, circuits),
        PATHS: lambda f: paths(f, circuits),
        TFIM: lambda f: tfim(f, circuits, True),
        TFIM_NON_PERIOD: lambda f: tfim(f, circuits, False),
        BASICS: lambda f: basics(f, circuits),
    }

    for part in parts_to_do:
        f = savepath.joinpath(f"{part}.csv")
        if skip_existing and f.exists():
            continue
        eval_functions[part](f)

    create_merged(savepath)


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

    print("loading file")
    with open(args.filename, "r") as f:
        circuits = json.load(f)

    print("parsing circuits")
    parsed_circuits: list[ParametrizedQuantumCircuit] = [parse_circuit(circuit) for circuit in circuits]

    evaluate(parsed_circuits, args.seed, args.savepath, args.skip_existing, to_do)
