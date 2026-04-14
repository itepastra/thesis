import logging
import random
from collections.abc import Callable

import numpy as np
import scipy
from numpy.random import Generator
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator
from tqdm import tqdm

from quantum_circuit import ParametrizedQuantumCircuit


def benchmark_qas(
    qas_results: list[ParametrizedQuantumCircuit],
    problem_function: Callable[[ParametrizedQuantumCircuit], tuple[bool, ...]],
    continue_after_found: bool = False,
):
    succes_data: list[tuple[ParametrizedQuantumCircuit, int, tuple[bool, ...]]] = []
    for i, circ in tqdm(enumerate(qas_results), desc="Circuit", leave=False):
        result = problem_function(circ)
        if result[0]:
            logging.info(f"Circ\n{circ}\nat index {i} succeeded")
            succes_data.append((circ, i, result))
            if not continue_after_found:
                break

    return succes_data


SHIFT = np.pi / 2.0


def parameter_shift(
    value: np.ndarray[tuple[int], np.dtype[np.float64]], shift_index: int, want_index: int
) -> tuple[float, float]:

    if want_index != shift_index:
        return float(value[want_index]), float(value[want_index])
    return float(value[want_index] + SHIFT), float(value[want_index] - SHIFT)


def optimize_circuit_adam(
    circ: ParametrizedQuantumCircuit,
    rng: Generator,
    backend: AerSimulator,
    hamiltonian,
    n_heads: int = 1000,
    steps: int = 1000,
    beta_1: float = 0.9,
    beta_2: float = 0.999,
    alpha: float = 0.001,
    epsilon: float = 1e-8,
    tpos: int = 1,
):

    qc, thetas = circ.circ
    tqc = transpile(qc, backend, optimization_level=2)
    p = circ.parameters

    theta: np.ndarray[tuple[int], np.dtype[np.float64]] = rng.uniform(-np.pi, np.pi, p)

    def energy_and_grad_fn(
        param_values: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> tuple[float, np.ndarray[tuple[int], np.dtype[np.float64]]]:
        result = backend.run(
            tqc,
            [
                {
                    param: [float(param_values[i])] + [a for k in range(p) for a in parameter_shift(param_values, k, i)]
                    for i, param in enumerate(thetas.params)
                }
            ],
        ).result()
        statevectors = np.asarray([result.get_statevector(i) for i in range(1 + 2 * p)], dtype=np.complex128)

        energies = [float(np.real(np.vdot(sv, hamiltonian @ sv))) for sv in statevectors]

        grad = np.zeros(p, dtype=np.float64)
        for i in range(p):
            grad[i] = 0.5 * (energies[2 * i + 1] - energies[2 * i + 2])

        return energies[0], grad

    best_theta = None
    best_energy = np.inf
    history: list[list[float]] = []

    for head in tqdm(range(n_heads), desc="Optimizing head", leave=False, position=tpos):
        params = rng.uniform(-np.pi, np.pi, p)
        m = np.zeros_like(params)
        v = np.zeros_like(params)
        head_history: list[float] = []

        for t in tqdm(range(1, steps + 1), desc="Optimisation step", leave=False, position=tpos + 1):
            energy, grad = energy_and_grad_fn(params)
            head_history.append(energy)

            m = beta_1 * m + (1 - beta_1) * grad
            v = beta_2 * v + (1 - beta_2) * grad * grad

            m_corr = m / (1 - beta_1**t)
            v_corr = v / (1 - beta_2**t)

            params -= alpha * m_corr / (np.sqrt(v_corr) + epsilon)

        history.append(head_history)

    return best_theta, best_energy, history
