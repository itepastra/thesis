from dataclasses import dataclass
import math
import random
from typing import override
import numpy as np
from enum import IntEnum

from qiskit import QuantumCircuit as QiskitCircuit, transpile
from qiskit.circuit import ParameterVector, ParameterVectorElement
from qiskit_aer import AerSimulator


class GateType(IntEnum):
    """
    Enum of various (parametrized) gates
    """

    RX = 1
    RY = 2
    RZ = 3
    RXX = 4
    RYY = 5
    RZZ = 6
    CX = 7
    CZ = 8
    CRX = 9
    H = 10
    I = 11


def single_typ(typ: GateType) -> bool:
    match typ:
        case GateType.I | GateType.H | GateType.RX | GateType.RY | GateType.RZ:
            return True
        case (
            GateType.RXX
            | GateType.RYY
            | GateType.RZZ
            | GateType.CX
            | GateType.CZ
            | GateType.CRX
        ):
            return False


@dataclass(frozen=True)
class Gate:
    typ: GateType
    qubits: int | tuple[int, int]
    param_idx: int

    def to_json(self):
        return {
            "type": int(self.typ),
            "qubits": self.qubits,
            "param_idx": self.param_idx,
        }

    def single(self) -> bool:
        return single_typ(self.typ)


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
                if gate.typ <= 3 or isinstance(gate.qubits, int):
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
                if gate.typ == GateType.RX:
                    theta = thetas[gate.param_idx]
                    qc.rx(theta, gate.qubits)
                elif gate.typ == GateType.RY:
                    theta = thetas[gate.param_idx]
                    qc.ry(theta, gate.qubits)
                elif gate.typ == GateType.RZ:
                    theta = thetas[gate.param_idx]
                    qc.rz(theta, gate.qubits)
                elif gate.typ == GateType.H:
                    qc.h(gate.qubits)
                elif gate.typ == GateType.I:
                    qc.id(gate.qubits)
                elif gate.typ == GateType.RXX:
                    theta = thetas[gate.param_idx]
                    qc.rxx(theta, *gate.qubits)
                elif gate.typ == GateType.RYY:
                    theta = thetas[gate.param_idx]
                    qc.ryy(theta, *gate.qubits)
                elif gate.typ == GateType.RZZ:
                    theta = thetas[gate.param_idx]
                    qc.rzz(theta, *gate.qubits)
                elif gate.typ == GateType.CX:
                    qc.cx(*gate.qubits)
                elif gate.typ == GateType.CRX:
                    theta = thetas[gate.param_idx]
                    qc.crx(theta, *gate.qubits)
                else:
                    raise ValueError(f"Unknown gate type: {gate.typ}")
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
                param: [rng.random() * math.tau for _ in range(nexp)]
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
                match gate.typ:
                    case GateType.RX:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RX"
                    case GateType.RY:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RY"
                    case GateType.RZ:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "RZ"
                    case GateType.RXX:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"X{idx}"
                        strs[q2] = strs[q2][:-2] + f"X{idx}"
                        idx += 1
                    case GateType.RYY:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"Y{idx}"
                        strs[q2] = strs[q2][:-2] + f"Y{idx}"
                        idx += 1
                    case GateType.RZZ:
                        (q1, q2) = gate.qubits
                        strs[q1] = strs[q1][:-2] + f"Z{idx}"
                        strs[q2] = strs[q2][:-2] + f"Z{idx}"
                        idx += 1
                    case GateType.CX:
                        (c, t) = gate.qubits
                        strs[c] = strs[c][:-2] + f"C{idx}"
                        strs[t] = strs[t][:-2] + f"X{idx}"
                        idx += 1
                    case GateType.CRX:
                        (c, t) = gate.qubits
                        strs[c] = strs[c][:-2] + f"C{idx}"
                        strs[t] = strs[t][:-2] + f"R{idx}"
                        idx += 1
                    case GateType.CZ:
                        (c, t) = gate.qubits
                        strs[c] = strs[c][:-2] + f"C{idx}"
                        strs[t] = strs[t][:-2] + f"Z{idx}"
                        idx += 1
                    case GateType.H:
                        strs[gate.qubits] = strs[gate.qubits][:-2] + "H-"

        gt = ""
        if self.gt_energy is not None:
            gt = f"\nGT: E={self.gt_energy:.12f}, err={self.gt_error:.3e}, steps={self.gt_steps}, success={self.gt_success}"
        return (
            "\n".join(strs)
            + f"\npaths: {self.paths}, expressibility: {self.expressibility}, params: {self.params}"
            + gt
        )


def even_parity(qubits: int):
    return [(x, x + 1) for x in range(0, qubits, 2)]


def odd_parity(qubits: int):
    return [(x, x + 1) for x in range(1, qubits, 2)]


def sample_circuit_layers(
    rng: random.Random, qubits: int, depth: int
) -> QuantumCircuit:
    even = even_parity(qubits)
    odd = odd_parity(qubits)

    total_single = 0
    total_double = 0
    params = 0

    gates: list[list[Gate]] = []
    for _ in range(depth):
        if total_single + total_double >= 36:
            break

        gate_locations = even if rng.random() < 0.5 else odd

        layer = []
        for loc in gate_locations:
            gate_type = rng.randint(1, 6)
            if gate_type >= 4:
                if loc[1] == qubits:
                    continue
                layer.append(Gate(GateType(gate_type), loc, params))
                total_double += 1
            else:
                layer.append(Gate(GateType(gate_type), loc[0], params))
                total_single += 1
        gates.append(layer)
        params += 1

    return QuantumCircuit(qubits, gates, total_single, total_double, params)


def sample_layers_generator(rng: random.Random, qubits: int, depth: int):
    while True:
        yield sample_circuit_layers(rng, qubits, depth)


def circ_from_layers(layers: list[list[Gate]], qubits: int) -> QuantumCircuit:
    params = 0
    total_single = 0
    total_double = 0
    gates: list[list[Gate]] = []

    for layer in layers:
        new_layer = []
        for gate in layer:
            match gate.typ:
                case GateType.H:
                    new_layer.append(Gate(gate.typ, gate.qubits, params))
                    total_single += 1
                case GateType.RX | GateType.RY | GateType.RZ:
                    new_layer.append(Gate(gate.typ, gate.qubits, params))
                    params += 1
                    total_single += 1
                case GateType.RXX | GateType.RYY | GateType.RZZ:
                    new_layer.append(Gate(gate.typ, gate.qubits, params))
                    params += 1
                    total_double += 1
                case GateType.CX | GateType.CZ:
                    new_layer.append(Gate(gate.typ, gate.qubits, params))
                    total_double += 1
                case GateType.CRX:
                    new_layer.append(Gate(gate.typ, gate.qubits, params))
                    params += 1
                    total_double += 1
        gates.append(new_layer)
    return QuantumCircuit(qubits, gates, total_single, total_double, params)


def sample_circuit_random(
    rng: random.Random, qubits: int, depth: int, gate_types: list[GateType]
) -> QuantumCircuit:
    params = 0
    total_single = 0
    total_double = 0
    gates: list[list[Gate]] = []
    for _ in range(depth):
        used_qubits: set[int] = set()
        layer: list[Gate] = []

        for loc in range(qubits):
            if loc in used_qubits:
                continue
            gate_type = rng.choice(
                gate_types
                if loc + 1 < qubits
                else [typ for typ in gate_types if single_typ(typ)]
            )
            match gate_type:
                case GateType.H:
                    layer.append(Gate(gate_type, loc, params))
                    total_single += 1
                    used_qubits.add(loc)
                case GateType.RX | GateType.RY | GateType.RZ:
                    layer.append(Gate(gate_type, loc, params))
                    params += 1
                    total_single += 1
                    used_qubits.add(loc)
                case GateType.RXX | GateType.RYY | GateType.RZZ:
                    layer.append(Gate(gate_type, (loc, loc + 1), params))
                    params += 1
                    total_double += 1
                    used_qubits.add(loc)
                    used_qubits.add(loc + 1)
                case GateType.CX | GateType.CZ:
                    layer.append(
                        Gate(
                            gate_type,
                            (loc, loc + 1) if rng.random() < 0.5 else (loc + 1, loc),
                            params,
                        )
                    )
                    total_double += 1
                    used_qubits.add(loc)
                    used_qubits.add(loc + 1)
                case GateType.CRX:
                    layer.append(
                        Gate(
                            gate_type,
                            (loc, loc + 1) if rng.random() < 0.5 else (loc + 1, loc),
                            params,
                        )
                    )
                    params += 1
                    total_double += 1
                    used_qubits.add(loc)
                    used_qubits.add(loc + 1)
                case _:
                    pass
        gates.append(layer)

    return QuantumCircuit(qubits, gates, total_single, total_double, params)


def sample_random_generator(
    rng: random.Random, qubits: int, depth: int, gates: list[GateType]
):
    while True:
        yield sample_circuit_random(rng, qubits, depth, gates)
