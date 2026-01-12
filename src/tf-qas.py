#!/usr/bin/env python
import json
from dataclasses import dataclass
from enum import IntEnum
from multiprocessing import Pool
import random
import numpy as np
from typing import override
from qiskit.circuit import ParameterVector
from tqdm import tqdm
from qiskit import QuantumCircuit as QiskitCircuit, transpile
from qiskit_aer import AerSimulator

from qas_flow import Stream

TWO_QUBIT_GATE_PROBABILITY = 0.5


class GateType(IntEnum):
    RX = 1
    RY = 2
    RZ = 3
    XX = 4
    YY = 5
    ZZ = 6


@dataclass(frozen=True)
class Gate:
    type: GateType
    qubits: int | tuple[int, int]
    param_idx: int

    def to_json(self):
        return {"type": self.type, "qubits": self.qubits, "param_idx": self.param_idx}


def haar_fidelity_pdf(F: np.ndarray, d: int) -> np.ndarray:
    # p(F) = (d-1) * (1-F)^(d-2), for F in [0,1]
    return (d - 1) * np.power(1.0 - F, d - 2)


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    # assumes p, q are normalized and strictly positive
    return float(np.sum(p * np.log(p / q)))


@dataclass()
class QuantumCircuit:
    qubits: int
    gates: list[list[Gate]]
    single_qubit_gates: int
    two_qubit_gates: int
    params: int
    paths: int = 0
    expressibility: float = float("-inf")

    def calculate_paths(self):
        path_counts = [1 for _ in range(self.qubits)]
        for layer in self.gates:
            for gate in layer:
                if gate.type <= 3 or type(gate.qubits) is int:
                    continue
                (q1, q2) = gate.qubits
                path_counts[q1] = path_counts[q1] + path_counts[q2]
                path_counts[q2] = path_counts[q1]

        self.paths = sum(path_counts)

    def to_json(self):
        return {
            "qubits": self.qubits,
            "gates": [[gate.to_json() for gate in layer] for layer in self.gates],
            "params": self.params,
            "paths": self.paths,
            "expressibility": self.expressibility,
        }

    def to_qiskit(self):
        qc = QiskitCircuit(self.qubits)
        thetas = ParameterVector("theta", self.params)

        for layer in self.gates:
            for gate in layer:
                theta = thetas[gate.param_idx]
                if gate.type == GateType.RX:
                    qc.rx(theta, gate.qubits)
                elif gate.type == GateType.RY:
                    qc.ry(theta, gate.qubits)
                elif gate.type == GateType.RZ:
                    qc.rz(theta, gate.qubits)
                elif gate.type == GateType.XX:
                    qc.rxx(theta, *gate.qubits)
                elif gate.type == GateType.YY:
                    qc.ryy(theta, *gate.qubits)
                elif gate.type == GateType.ZZ:
                    qc.rzz(theta, *gate.qubits)
        qc.save_statevector()
        return qc, thetas

    def expressibility_estimate(
        self, samples: int, seed: int, bins: int = 75, eps: float = 1e-12
    ):
        qc, thetas = self.to_qiskit()

        if self.params <= 0:
            return float("inf")

        rng = random.Random(seed)
        d = 1 << self.qubits

        backend = AerSimulator(method="statevector", seed_simulator=seed)

        tqc = transpile(qc, backend, optimization_level=0)

        nexp = 2 * samples

        binds = [
            {param: [rng.random() for _ in range(nexp)] for param in thetas.params}
        ]

        job = backend.run([tqc], parameter_binds=binds)
        result = job.result()

        sv = [
            np.asarray(result.get_statevector(i), dtype=np.complex128)
            for i in range(nexp)
        ]
        left = sv[:samples]
        right = sv[samples:]

        inners = np.array(
            [np.vdot(l, r) for l, r in zip(left, right)], dtype=np.complex128
        )
        F = (inners.conjugate() * inners).real

        # 4) empirical histogram (as a probability mass over bins)
        hist, edges = np.histogram(F, bins=bins, range=(0.0, 1.0), density=False)
        p = hist.astype(np.float64)
        p = p + eps
        p = p / p.sum()

        # 5) Haar distribution mass per bin (integrate PDF over each bin)
        # approximate via midpoint rule
        mids = 0.5 * (edges[:-1] + edges[1:])
        widths = edges[1:] - edges[:-1]
        q = haar_fidelity_pdf(mids, d) * widths
        q = q + eps
        q = q / q.sum()

        kl = kl_divergence(p, q)
        self.expressibility = -kl
        return self

    @override
    def __str__(self):
        strs = ["-" for _ in range(self.qubits)]
        for layer in self.gates:
            for i in range(self.qubits):
                strs[i] += "---"

            idx = 0

            for gate in layer:
                match gate.type:
                    case GateType.RX:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RX"
                    case GateType.RY:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RY"
                    case GateType.RZ:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RZ"
                    case GateType.XX:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"X{idx}"
                        strs[q2] = strs[q2][:-2] + f"X{idx}"
                        idx += 1
                    case GateType.YY:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"Y{idx}"
                        strs[q2] = strs[q2][:-2] + f"Y{idx}"
                        idx += 1
                    case GateType.ZZ:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"Z{idx}"
                        strs[q2] = strs[q2][:-2] + f"Z{idx}"
                        idx += 1
        return (
            "\n".join(strs)
            + f"\npaths: {self.paths}, expressibility: {self.expressibility}"
        )


def even_parity(qubits: int):
    return [(x, x + 1) for x in range(0, qubits, 2)]


def odd_parity(qubits: int):
    return [(x, x + 1) for x in range(1, qubits, 2)]


def sample_circuit(rng: random.Random, qubits: int, depth: int) -> QuantumCircuit:
    even = even_parity(qubits)
    odd = odd_parity(qubits)

    total_single = 0
    total_double = 0
    params = 0

    gates: list[list[Gate]] = []
    for _ in range(depth):
        gate_type_offset = 3 if rng.random() < TWO_QUBIT_GATE_PROBABILITY else 0
        gate_type = rng.randint(1, 3)
        gate_locations = even if rng.random() < 0.5 else odd
        if gate_type_offset == 0:
            gates.append(
                [Gate(GateType(gate_type), x, params) for (x, _) in gate_locations]
            )
            total_single += len(gate_locations)
        else:
            gates.append(
                [
                    Gate(GateType(gate_type + gate_type_offset), xy, params)
                    for xy in gate_locations
                    if xy[1] != qubits
                ]
            )
            total_double += len(gate_locations)
        params += 1
    return QuantumCircuit(qubits, gates, total_single, total_double, params)


def sample_generator(rng: random.Random, qubits: int, depth: int):
    while True:
        yield sample_circuit(rng, qubits, depth)


def more_single_than_double(qc: QuantumCircuit) -> bool:
    return qc.single_qubit_gates >= qc.two_qubit_gates


if __name__ == "__main__":
    rng = random.Random()
    qubits = 4
    depth = 15
    sample_amount = 50000
    expressibility_samples = 2000
    proxy_pass_amount = 5000
    circuits = (
        Stream(sample_generator(rng, qubits, depth))
        .filter(more_single_than_double)
        .take(sample_amount)
        .collect()
    )
    for circuit in tqdm(circuits):
        circuit.calculate_paths()
    circuits.sort(key=lambda qc: qc.paths, reverse=True)
    seeds = [rng.randint(0, 1000000000) for _ in range(proxy_pass_amount)]

    def starmap_func(args):
        (circ, seed, idx) = args
        res = circ.expressibility_estimate(expressibility_samples, seed)
        return res

    final_circuits: list[QuantumCircuit] = []
    with Pool() as p:
        for circ in tqdm(
            p.imap_unordered(
                starmap_func,
                zip(circuits[:proxy_pass_amount], seeds, range(proxy_pass_amount)),
            ),
            total=proxy_pass_amount,
        ):
            final_circuits.append(circ)

    final_circuits.sort(key=lambda qc: qc.expressibility, reverse=True)
    for i, circuit in enumerate(final_circuits[::-1]):
        print(f"circuit {i}:\n{circuit}")

    with open("dump.json", "w+") as fp:
        json.dump([c.to_json() for c in final_circuits], fp, indent=4)
