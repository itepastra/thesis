from collections.abc import Callable

import jax
import numpy as np
import scipy
import tensorcircuit as tc
from numpy.random import Generator
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator

from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType
from quantum_circuit.tensorcircuit_helpers import build_tensor_circuit_factory

from . import optimize_circuit_adam

tc.set_backend("tensorflow")

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


def tfim_hamiltonian(n: int, periodic: bool = True):
    hamiltonian2 = tc.quantum.heisenberg_hamiltonian(
        tc.templates.graphs.Line1D(n, pbc=periodic), hzz=1, hxx=1, hyy=1, hx=0, hy=0, hz=1, sparse=False
    ).numpy()

    return hamiltonian2


def exact_ground_energy(hamiltonian: np.ndarray[tuple[int, int], np.dtype[np.float64]]) -> float:
    w = np.linalg.eigvalsh(hamiltonian)
    return float(w[0])




def make_problem_function(
    qubits: int,
    periodic: bool = True,  # make the first and last node connect or not
    success_accuracy: float = 0.01,  # within 1%
    seed: int | None = None,
    tpos: int = 1,
) -> tuple[Callable[[ParametrizedQuantumCircuit, int], tuple[bool, float]], float]:

    rng = np.random.default_rng(seed)

    hamiltonian = tfim_hamiltonian(qubits, periodic)
    true_energy = exact_ground_energy(hamiltonian)

    def tfim_problem(circ: ParametrizedQuantumCircuit, tpos_offset: int) -> tuple[bool, float]:

        tcirc_function = build_tensor_circuit_factory(
            circ, [QuantumGate(QuantumType.Hadamard, (i,)) for i in range(circ.qubits)], hamiltonian
        )

        vec_value_and_grad = tc.backend.jit(tc.backend.vectorized_value_and_grad(tcirc_function))
        best_params, best_energy = optimize_circuit_adam(circ, vec_value_and_grad, tpos=tpos + tpos_offset)

        return (
            bool(np.any(true_energy * (1 - success_accuracy) < best_energy < true_energy * (1 + success_accuracy))),
            best_energy,
        )

    return tfim_problem, true_energy
