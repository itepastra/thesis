import numpy as np
import scipy
from numpy.random import Generator
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator

from quantum_circuit import ParametrizedQuantumCircuit

dt = np.dtype(np.float64)
tau = np.pi * 2


def _pauli_x() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=dt)


def _pauli_z() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=dt)


def _ident() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.eye(2, dtype=dt)


def kronecker_product(
    gates: list[np.ndarray[tuple[int, int], np.dtype[np.float64]]],
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    out: np.ndarray[tuple[int, int], np.dtype[np.float64]] = np.array([[1.0]], dtype=dt)
    for op in gates:
        out = np.kron(out, op)
    return out


def tfim_hamiltonian(
    n: int, periodic: bool = True
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    X = _pauli_x()
    Z = _pauli_z()
    I = _ident()
    dimension = 1 << n
    H = np.zeros((dimension, dimension), dtype=dt)

    for i in range(n):
        operations = [I] * n
        operations[i] = X
        H += kronecker_product(operations)

        j = (i + 1) % n
        if (not periodic) and (j == 0):
            continue
        operations[i] = Z
        operations[j] = Z
        H += kronecker_product(operations)

    return H


def exact_ground_energy(H: np.ndarray[tuple[int, int], np.dtype[np.float64]]) -> float:
    w = np.linalg.eigvalsh(H)
    return float(w[0])


SHIFT = np.pi / 2.0


def pshift(val, idx):
    vp = val.copy()
    vm = val.copy()

    vp[idx] += SHIFT
    vm[idx] -= SHIFT

    return vp, vm


def optimize_circuit(circ: ParametrizedQuantumCircuit, rng: Generator, backend: AerSimulator):
    params = np.random.uniform(-np.pi, np.pi, (circ.parameters))

    qc, thetas = circ.circ
    tqc = transpile(qc, backend, optimization_level=2)
    p = circ.parameters

    theta = rng.uniform(-np.pi, np.pi, p)

    def energy_and_grad_fn(param_values: np.ndarray):
        bound = tqc.assign_parameters(
            {
                param: [val] + [a for k in range(p) for a in pshift(val, k)]
                for param, val in zip(thetas.params, param_values)
            }
        )
        result = backend.run(bound).result()
