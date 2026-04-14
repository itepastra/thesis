from collections.abc import Callable

import numpy as np
import scipy
from numpy.random import Generator
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator

from problems import optimize_circuit_adam
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


def tfim_hamiltonian(n: int, periodic: bool = True) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
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


def make_problem_function(
    qubits: int,
    periodic: bool = True,  # make the first and last node connect or not
    success_accuracy: float = 0.01,  # within 1%
    seed: int | None = None,
) -> Callable[[ParametrizedQuantumCircuit], tuple[bool, ...]]:

    rng = np.random.default_rng(seed)
    backend = AerSimulator(method="statevector")

    hamiltonian = tfim_hamiltonian(qubits, periodic)
    true_energy = exact_ground_energy(hamiltonian)

    def tfim_problem(pqc: ParametrizedQuantumCircuit) -> tuple[bool, ...]:
        best_params, best_energy, history = optimize_circuit_adam(pqc, rng, backend, hamiltonian)

        return (
            true_energy * (1 - success_accuracy) < best_energy < true_energy * (1 + success_accuracy),
            best_params,
            history,
        )

    return tfim_problem
