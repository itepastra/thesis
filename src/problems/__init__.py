import enum
import logging
import random
from collections.abc import Callable

import numpy as np
import scipy
import tensorcircuit as tc
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
    grad_tol=1e-5,
    energy_tol=1e-6,
    patience=20,
):

    qc, thetas = circ.circ
    tqc = transpile(qc, backend, optimization_level=2)
    p = circ.parameters

    theta: np.ndarray[tuple[int], np.dtype[np.float64]] = rng.uniform(-np.pi, np.pi, p)

    def energy_and_grad_fn(
        param_values: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    ) -> tuple[np.ndarray[tuple[int], np.dtype[np.float64]], np.ndarray[tuple[int, int], np.dtype[np.float64]]]:

        n_heads, p_local = param_values.shape
        assert p_local == p

        batch = np.repeat(param_values[:, None, :], 1 + 2 * p, axis=1)

        for i in range(p):
            batch[:, 2 * i + 1, i] += SHIFT
            batch[:, 2 * i + 2, i] -= SHIFT

        flat_batch = batch.reshape(-1, p)
        parameter_binds = {param: list(flat_batch[:, i]) for i, param in enumerate(thetas)}

        result = backend.run(tqc, [parameter_binds]).result()
        statevectors = np.asarray([result.get_statevector(i) for i in range(flat_batch.shape[0])], dtype=np.complex128)

        flat_energies = np.asarray([np.real(np.vdot(sv, hamiltonian @ sv)) for sv in statevectors], dtype=np.float64)
        energies_all = flat_energies.reshape(n_heads, 1 + 2 * p)
        energies = energies_all[:, 0]  # get the energies at all the parameter values

        grads = 0.5 * (energies_all[:, 1::2] - energies_all[:, 2::2])
        return energies, grads

    best_theta = None
    best_energy = np.inf
    history: list[list[float]] = []

    active = np.ones(n_heads, dtype=bool)
    best_seen = np.full(n_heads, np.inf)
    stall_count = np.zeros(n_heads, dtype=np.int32)

    params = rng.uniform(-np.pi, np.pi, (n_heads, p))
    m = np.zeros_like(params)
    v = np.zeros_like(params)

    bar = tqdm(
        range(1, steps + 1), desc=f"Optimization step (active: {np.count_nonzero(active)})", leave=False, position=tpos
    )
    for t in bar:
        bar.desc = f"Optimization step (active: {np.count_nonzero(active)})"
        if not np.any(active):
            break
        active_idx = np.where(active)[0]
        energies, grads = energy_and_grad_fn(params[active_idx])
        history.append(list(energies))

        improved = energies < (best_seen[active_idx] - energy_tol)
        best_seen[active_idx[improved]] = energies[improved]

        stall_count[active_idx[improved]] = 0
        stall_count[active_idx[~improved]] += 1

        grad_norm = np.linalg.norm(grads, axis=1)
        done = (grad_norm < grad_tol) | (stall_count[active_idx] >= patience)
        m_sub = m[active_idx]
        v_sub = v[active_idx]

        m_sub = beta_1 * m_sub + (1 - beta_1) * grads
        v_sub = beta_2 * v_sub + (1 - beta_2) * grads * grads

        m_corr = m_sub / (1 - beta_1**t)
        v_corr = v_sub / (1 - beta_2**t)

        params[active_idx[~done]] -= alpha * m_corr[~done] / (np.sqrt(v_corr[~done]) + epsilon)

        m[active_idx] = m_sub
        v[active_idx] = v_sub
        active[active_idx[done]] = False

    return best_theta, best_energy, history
