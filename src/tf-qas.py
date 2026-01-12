#!/usr/bin/env python
from __future__ import annotations
import argparse
from itertools import repeat
import json
import math
import random
from dataclasses import dataclass
from enum import IntEnum
from multiprocessing import Pool
from typing import override
import numpy as np
from qiskit import QuantumCircuit as QiskitCircuit, transpile
from qiskit.circuit import ParameterVector, ParameterVectorElement
from qiskit_aer import AerSimulator
from tqdm import tqdm

from qas_flow import Stream

# ----------------------------
# Paper hyperparameters/defaults
# ----------------------------

TWO_QUBIT_GATE_PROBABILITY = 0.5
CHEMICAL_ACCURACY = 1.6e-3  # Ha, success if E - E0 <= this

# ----------------------------
# Circuit representation
# ----------------------------


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
        return {
            "type": int(self.type),
            "qubits": self.qubits,
            "param_idx": self.param_idx,
        }


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

    # ground-truth fields (filled later)
    gt_energy: float | None = None
    gt_error: float | None = None
    gt_steps: int | None = None
    gt_success: bool | None = None

    def calculate_paths(self):
        path_counts = [1 for _ in range(self.qubits)]
        for layer in self.gates:
            for gate in layer:
                if gate.type <= 3 or isinstance(gate.qubits, int):
                    continue
                (q1, q2) = gate.qubits
                # same logic as your existing file
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
            "gt_energy": self.gt_energy,
            "gt_error": self.gt_error,
            "gt_steps": self.gt_steps,
            "gt_success": self.gt_success,
        }

    def to_qiskit_ansatz(self) -> tuple[QiskitCircuit, ParameterVector]:
        """Return *just* the parametrized ansatz defined by this circuit."""
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
                else:
                    raise ValueError(f"Unknown gate type: {gate.type}")
        return qc, thetas

    def to_qiskit_for_expressibility(self) -> tuple[QiskitCircuit, ParameterVector]:
        """Expressibility uses |0...0> input (no TFIM-specific H layer)."""
        qc, thetas = self.to_qiskit_ansatz()
        qc.save_statevector()
        return qc, thetas

    def to_qiskit_for_tfim_vqe(self) -> tuple[QiskitCircuit, ParameterVector]:
        """TFIM VQE begins with a layer of Hadamards on all qubits."""
        ans, thetas = self.to_qiskit_ansatz()
        qc = QiskitCircuit(self.qubits)
        qc.h(range(self.qubits))
        qc.compose(ans, inplace=True)
        qc.save_statevector()
        return qc, thetas

    def expressibility_estimate(
        self, samples: int, seed: int, bins: int = 75, eps: float = 1e-12
    ) -> "QuantumCircuit":
        qc, thetas = self.to_qiskit_for_expressibility()

        if self.params <= 0:
            self.expressibility = float("-inf")
            return self

        rng = random.Random(seed)
        d = 1 << self.qubits

        backend = AerSimulator(method="statevector", seed_simulator=seed)
        tqc = transpile(qc, backend, optimization_level=0)

        nexp = 2 * samples
        # vectorized binds: one circuit, many parameter values
        binds: list[dict[ParameterVectorElement, list[float]]] = [
            {
                param: [rng.random() * 4 * math.pi - 2 * math.pi for _ in range(nexp)]
                for param in thetas.params
            }
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

        hist, edges = np.histogram(F, bins=bins, range=(0.0, 1.0), density=False)
        p = hist.astype(np.float64) + eps
        p = p / p.sum()

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
        gt = ""
        if self.gt_energy is not None:
            gt = f"\nGT: E={self.gt_energy:.12f}, err={self.gt_error:.3e}, steps={self.gt_steps}, success={self.gt_success}"
        return (
            "\n".join(strs)
            + f"\npaths: {self.paths}, expressibility: {self.expressibility}"
            + gt
        )


# ----------------------------
# Search space sampling (layerwise)
# ----------------------------


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
        if total_single + total_double >= 36:
            break
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


# ----------------------------
# TFIM ground-truth VQE
# ----------------------------


def _pauli_x():
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)


def _pauli_z():
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)


def _eye():
    return np.eye(2, dtype=np.float64)


def kron_n(ops: list[np.ndarray]) -> np.ndarray:
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def tfim_hamiltonian_matrix(n: int, periodic: bool = True) -> np.ndarray:
    """
    HTFIM = sum_{i=1}^n Z_i Z_{i+1} + X_i  (paper definition) :contentReference[oaicite:5]{index=5}
    with Z_{n+1}=Z_1 if periodic.
    """
    X = _pauli_x()
    Z = _pauli_z()
    I = _eye()
    dim = 1 << n
    H = np.zeros((dim, dim), dtype=np.float64)

    # Xi terms
    for i in range(n):
        ops = [I] * n
        ops[i] = X
        H += kron_n(ops)

    # Zi Zi+1 terms
    for i in range(n):
        j = (i + 1) % n
        if (not periodic) and (j == 0):
            continue
        ops = [I] * n
        ops[i] = Z
        ops[j] = Z
        H += kron_n(ops)

    return H


def exact_ground_energy(H: np.ndarray) -> float:
    # H is real symmetric here
    w = np.linalg.eigvalsh(H)
    return float(w[0])


def statevector_from_bound_circuit(
    backend: AerSimulator, tqc: QiskitCircuit, bind: dict
) -> np.ndarray:
    res = backend.run([tqc], parameter_binds=[bind]).result()
    sv = np.asarray(res.get_statevector(0), dtype=np.complex128)
    return sv


def energy_expectation_from_sv(H: np.ndarray, sv: np.ndarray) -> float:
    # E = <psi|H|psi>
    # H real symmetric; sv complex
    return float(np.real(np.vdot(sv, H @ sv)))


def adam_optimize_tfim_energy(
    circuit: QuantumCircuit,
    H: np.ndarray,
    seed: int,
    lr: float = 0.01,  # paper :contentReference[oaicite:6]{index=6}
    max_steps: int = 2000,
    tol: float = 1e-7,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    param_shift: float = math.pi / 2,
) -> tuple[float, int]:
    """
    Optimize parameters with Adam using parameter-shift gradients.
    Returns: (best_energy, steps_taken)
    """
    qc, thetas = circuit.to_qiskit_for_tfim_vqe()

    p = circuit.params
    rng = np.random.default_rng(seed)
    theta = rng.uniform(
        -2 * math.pi, 2 * math.pi, size=p
    )  # paper init range :contentReference[oaicite:7]{index=7}

    backend = AerSimulator(method="statevector", seed_simulator=seed)
    tqc = transpile(qc, backend, optimization_level=0)

    def E(th: np.ndarray) -> float:
        bind = {param: [val] for param, val in zip(thetas.params, th)}
        sv = statevector_from_bound_circuit(backend, tqc, bind)
        return energy_expectation_from_sv(H, sv)

    def grad(th: np.ndarray) -> np.ndarray:
        # parameter-shift: d/dθ f(θ) = 0.5*(f(θ+π/2)-f(θ-π/2))
        g = np.zeros_like(th)
        for i in range(p):
            plus = th.copy()
            minus = th.copy()
            plus[i] += param_shift
            minus[i] -= param_shift
            g[i] = 0.5 * (E(plus) - E(minus))
        return g

    m = np.zeros_like(theta)
    v = np.zeros_like(theta)

    best_E = float("inf")
    prev_E = None

    for t in range(1, max_steps + 1):
        g = grad(theta)
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * (g * g)
        mhat = m / (1 - beta1**t)
        vhat = v / (1 - beta2**t)
        theta = theta - lr * mhat / (np.sqrt(vhat) + eps)

        cur_E = E(theta)
        if cur_E < best_E:
            best_E = cur_E

        if prev_E is not None and abs(prev_E - cur_E) < tol:
            return best_E, t
        prev_E = cur_E

    return best_E, max_steps


def ground_truth_tfim(
    circ: QuantumCircuit,
    H: np.ndarray,
    E0: float,
    seed: int,
    lr: float,
    max_steps: int,
    tol: float,
) -> QuantumCircuit:
    best_E, steps = adam_optimize_tfim_energy(
        circ, H, seed=seed, lr=lr, max_steps=max_steps, tol=tol
    )
    err = best_E - E0
    circ.gt_energy = best_E
    circ.gt_error = err
    circ.gt_steps = steps
    circ.gt_success = err <= CHEMICAL_ACCURACY
    return circ


# ----------------------------
# Main
# ----------------------------


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--qubits",
        type=int,
        default=6,
        help="TFIM qubit count (paper uses 6). :contentReference[oaicite:8]{index=8}",
    )
    ap.add_argument(
        "--depth",
        type=int,
        default=10,
        help="Max depth for TFIM layerwise (paper max depth 10). :contentReference[oaicite:9]{index=9}",
    )
    ap.add_argument(
        "--sample_amount",
        type=int,
        default=50000,
        help="Number of sampled circuits (paper uses 50,000). :contentReference[oaicite:10]{index=10}",
    )
    ap.add_argument(
        "--expressibility_samples",
        type=int,
        default=2000,
        help="Fidelity samples for expressibility (paper uses 2000). :contentReference[oaicite:11]{index=11}",
    )
    ap.add_argument(
        "--proxy_pass_amount",
        type=int,
        default=5000,
        help="R: top circuits kept by paths (paper uses 5000). :contentReference[oaicite:12]{index=12}",
    )
    ap.add_argument(
        "--topk",
        type=int,
        default=100,
        help="K: how many top circuits to output/store.",
    )
    ap.add_argument(
        "--seed", type=int, default=0, help="RNG seed for sampling/reproducibility."
    )
    ap.add_argument(
        "--periodic",
        action="store_true",
        help="Use periodic TFIM boundary (default true if set).",
    )
    ap.add_argument(
        "--no-periodic",
        dest="periodic",
        action="store_false",
        help="Use open boundary TFIM.",
    )
    ap.set_defaults(periodic=True)

    # ground-truth options
    ap.add_argument(
        "--do_ground_truth",
        action="store_true",
        help="Also evaluate ground-truth TFIM VQE performance.",
    )
    ap.add_argument(
        "--gt_budget",
        type=int,
        default=100,
        help="Max number of circuits to query for ground-truth (paper often reports within 100 queries). :contentReference[oaicite:13]{index=13}",
    )
    ap.add_argument(
        "--gt_lr",
        type=float,
        default=0.01,
        help="Adam learning rate (paper uses 0.01). :contentReference[oaicite:14]{index=14}",
    )
    ap.add_argument(
        "--gt_max_steps",
        type=int,
        default=2000,
        help="Max Adam steps per circuit (practical cap).",
    )
    ap.add_argument(
        "--gt_tol",
        type=float,
        default=1e-7,
        help="Convergence tolerance for |E_t - E_{t-1}|.",
    )
    ap.add_argument("--dump", type=str, default="dump.json", help="Output JSON file.")

    return ap.parse_args()


def expr_worker(payload):
    circ, seed, samples = payload
    return circ.expressibility_estimate(samples, seed)


def main():
    args = parse_args()
    rng = random.Random(args.seed)

    # --- Stage 0: sample circuits
    circuits = (
        Stream(sample_generator(rng, args.qubits, args.depth))
        .filter(more_single_than_double)
        .take(args.sample_amount)
        .collect()
    )

    # --- Stage 1: paths
    for c in tqdm(circuits, desc="paths"):
        c.calculate_paths()
    circuits.sort(key=lambda qc: qc.paths, reverse=True)
    candidates = circuits[: args.proxy_pass_amount]

    # --- Stage 2: expressibility
    seeds = [rng.randint(0, 1_000_000_000) for _ in range(len(candidates))]

    final_circuits: list[QuantumCircuit] = []
    with Pool() as p:
        for circ in tqdm(
            p.imap_unordered(
                expr_worker, zip(candidates, seeds, repeat(args.expressibility_samples))
            ),
            total=len(candidates),
            desc="expressibility",
        ):
            final_circuits.append(circ)

    final_circuits.sort(key=lambda qc: qc.expressibility, reverse=True)

    # --- Ground-truth TFIM (optional): query from best to worst until success or budget
    success_idx = None
    if args.do_ground_truth:
        H = tfim_hamiltonian_matrix(args.qubits, periodic=args.periodic)
        E0 = exact_ground_energy(H)

        print(f"\nTFIM exact ground energy E0 = {E0:.12f}  (periodic={args.periodic})")

        gt_seed_stream = random.Random(args.seed + 1234567)
        queried = 0
        min_error = float("inf")
        for i, circ in enumerate(tqdm(final_circuits, desc="ground-truth queries")):
            if queried >= args.gt_budget:
                break
            seed = gt_seed_stream.randint(0, 1_000_000_000)
            ground_truth_tfim(
                circ,
                H,
                E0,
                seed=seed,
                lr=args.gt_lr,
                max_steps=args.gt_max_steps,
                tol=args.gt_tol,
            )
            if circ.gt_error is not None and circ.gt_error < min_error:
                print(f"new best error for {queried}: {circ.gt_error}")
            queried += 1
            if circ.gt_success:
                success_idx = i
                break

        if success_idx is None:
            print(f"\nNo circuit hit chemical accuracy within budget={args.gt_budget}.")
        else:
            print(f"\nFirst success at rank {success_idx} (0-based) within budget.")
            print(final_circuits[success_idx])

    # Print bottom few (worst) and top few (best) for sanity
    print("\nTop circuits (best expressibility):")
    for i, c in enumerate(final_circuits[: min(args.topk, 10)]):
        print(f"\nrank {i}:\n{c}")

    # Dump top-K (or all if you want)
    out = final_circuits[: args.topk]
    with open(args.dump, "w", encoding="utf-8") as fp:
        json.dump([c.to_json() for c in out], fp, indent=2)

    print(f"\nWrote {len(out)} circuits to {args.dump}.")


if __name__ == "__main__":
    main()
