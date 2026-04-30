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
from evaluator.problems.tfim import make_problem_function as make_tfim_problem
from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType
from quantum_circuit.proxy_config import ProxyConfig

BASICS = "basics"
EXPRESSIVITY = "expressivity"
PATHS = "paths"
TFIM = "tfim"
TFIM_NON_PERIOD = "tfim_non_period"
PRINTED = "printed"

EVAL_TARGET_TPOS = 2


def parse_circuit(circuit) -> ParametrizedQuantumCircuit:
    c = ParametrizedQuantumCircuit(circuit["qubits"])

    gates = [QuantumGate(QuantumType(gate["type"]), tuple(gate["qubits"])) for gate in circuit["gates"]]

    for gate in gates:
        c.append_gate(gate)
    c.check_parameters(False)

    return c


def expressivity(file: Path, circuits: list[ParametrizedQuantumCircuit], offset: int = 0):

    with open(file, "w+" if offset == 0 else "a") as f:
        if offset == 0:
            f.write("index,expressivity\n")
        for i, circ in tqdm(
            enumerate(circuits),
            total=len(circuits),
            leave=False,
            position=EVAL_TARGET_TPOS,
            desc=EXPRESSIVITY,
            colour="cyan",
        ):
            f.write(f"{i+offset},{circ.expressivity(ProxyConfig(circ.qubits))}\n")


def paths(file: Path, circuits: list[ParametrizedQuantumCircuit], offset: int = 0):
    from quantum_circuit.proxies.path import count_paths, make_dag

    def calc_paths(circ: ParametrizedQuantumCircuit) -> int:
        dag = make_dag(circ)
        node_count = len(dag)
        return count_paths(dag, 0, node_count - 1, [None for _ in range(node_count)])

    with open(file, "w+" if offset == 0 else "a") as f:
        if offset == 0:
            f.write("index,paths\n")
        for i, circ in tqdm(
            enumerate(circuits), total=len(circuits), leave=False, position=EVAL_TARGET_TPOS, desc=PATHS, colour="cyan"
        ):
            f.write(f"{i+offset},{calc_paths(circ)}\n")


def tfim(file: Path, circuits: list[ParametrizedQuantumCircuit], periodic: bool, offset: int = 0):

    with open(file, "w+" if offset == 0 else "a") as f:
        pfunc, true_energy = make_tfim_problem(circuits[0].qubits, periodic, tpos=EVAL_TARGET_TPOS + 1)
        benchmark_qas(
            circuits,
            pfunc,
            f,
            offset,
            true_energy,
            True,
            desc="periodic tfim" if periodic else "non periodic tfim",
            tpos=EVAL_TARGET_TPOS,
        )


def basics(file: Path, circuits: list[ParametrizedQuantumCircuit], offset: int = 0):
    with open(file, "w+" if offset == 0 else "a") as f:
        if offset == 0:
            f.write(f"index,depth,gates,parameters\n")
        for i, circ in tqdm(
            enumerate(circuits), total=len(circuits), leave=False, position=EVAL_TARGET_TPOS, desc=BASICS, colour="cyan"
        ):
            f.write(f"{i + offset},{len(circ.gates)},{sum(len(layer) for layer in circ.gates)},{circ.parameters}\n")


def printed_circuits(file: Path, circuits: list[ParametrizedQuantumCircuit], offset: int = 0):
    with open(file, "w+" if offset == 0 else "a") as f:
        for i, circ in enumerate(circuits):
            f.write(f"Circuit {i + offset}:\n{circ}\n\n\n")


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
    chunk_size: int = 25,
):
    print(f"setting up save folder at {savepath}")
    os.makedirs(savepath, exist_ok=True)

    eval_functions = {
        EXPRESSIVITY: expressivity,
        PATHS: paths,
        TFIM: lambda f, circs, offset: tfim(f, circs, True, offset),
        TFIM_NON_PERIOD: lambda f, circs, offset: tfim(f, circs, False, offset),
        BASICS: basics,
        PRINTED: printed_circuits,
    }

    extensions = {EXPRESSIVITY: "csv", PATHS: "csv", TFIM: "csv", TFIM_NON_PERIOD: "csv", BASICS: "csv", PRINTED: "txt"}

    for start in tqdm(range(0, len(circuits), chunk_size), desc="Chunk", leave=False, colour="red"):
        end = min(start + chunk_size, len(circuits))
        chunk_circuits = circuits[start:end]
        expected_indices = set(range(start, end))

        for part in tqdm(parts_to_do, desc="Eval Function", leave=False, position=1, colour="magenta"):
            f = savepath.joinpath(f"{part}.{extensions[part]}")

            if skip_existing and f.exists() and os.path.splitext(f)[1] == ".csv":
                df = pd.read_csv(f, usecols=["index"], comment="#")
                existing_indices = set(df["index"])

                # skip only if this chunk is fully present
                if expected_indices.issubset(existing_indices):
                    continue

            eval_functions[part](f, chunk_circuits, start)

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

    test_types = [TFIM, PATHS, EXPRESSIVITY, TFIM_NON_PERIOD, BASICS, PRINTED]
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
