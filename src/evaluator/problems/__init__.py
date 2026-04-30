import enum
import logging
import math
import multiprocessing
import random
from collections.abc import Callable
from io import TextIOWrapper
from itertools import repeat
from multiprocessing import Pool

import numpy as np
import scipy
import tensorflow as tf
from numpy.random import Generator
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator
from tqdm import tqdm

from quantum_circuit import ParametrizedQuantumCircuit


def log_circ_stats(file_handle: TextIOWrapper, i: int, result: tuple[bool, float], true_energy: float | None = None):
    file_handle.write(
        f"{i},{result[1]},{result[0]}{f",{(true_energy - result[1])/true_energy},{result[1] - true_energy}" if true_energy is not None else ""}\n"
    )


_problem_function = None
_worker_pos = None


def init_worker(counter):
    global _worker_pos
    with counter.get_lock():
        _worker_pos = counter.value
        counter.value += 1


def exec_problem_function(circ: ParametrizedQuantumCircuit) -> tuple[bool, float]:
    return _problem_function(circ, _worker_pos)


def benchmark_qas(
    qas_results: list[ParametrizedQuantumCircuit],
    problem_function: Callable[[ParametrizedQuantumCircuit, int], tuple[bool, float]],
    file_handle: TextIOWrapper,
    offset: int = 0,
    true_energy: float | None = None,
    continue_after_found: bool = False,
    tpos=0,
    desc="Circuit",
):
    global _problem_function
    _problem_function = problem_function
    succes_data: list[tuple[ParametrizedQuantumCircuit, int, tuple[bool, float]]] = []
    file_handle.write(
        f"# benchmaking {len(qas_results)} circuits{f", theoretical energy is {true_energy}" if true_energy is not None else ""}\n"
    )
    if offset == 0:
        file_handle.write(f"index,energy,succes{",error_rel,error_abs"if true_energy is not None else ""}\n")

    counter = multiprocessing.Value("i", 0)
    with Pool(initializer=init_worker, initargs=(counter,)) as p:
        for i, result in tqdm(
            enumerate(p.imap(exec_problem_function, qas_results)),
            total=len(qas_results),
            desc=desc,
            leave=False,
            colour="cyan",
        ):
            log_circ_stats(file_handle, i + offset, result, true_energy)
            if result[0]:
                succes_data.append((qas_results[i], i + offset, result))
                if not continue_after_found:
                    break

    return succes_data


def optimize_circuit_adam(
    circ: ParametrizedQuantumCircuit, vec_value_and_grad, batch_size: int = 1000, max_iter: int = 10000, tpos: int = 1
):
    param = tf.Variable(initial_value=tf.random.uniform(shape=[batch_size, circ.parameters]) * 2 * math.tau - math.tau)
    opt = tf.keras.optimizers.Adam(1e-2)
    bar = tqdm(range(max_iter), desc=f"Step (compiling)", leave=False, position=tpos, colour="green")
    e_last = np.full((batch_size,), np.inf)
    for i in bar:
        e, grad = vec_value_and_grad(param)
        opt.apply_gradients([(grad, param)])
        bar.desc = f"Step (current energy {np.min(e):.4f})"
        if i % 100 == 0:  # check if converged
            distance = np.abs(e_last - e.numpy())
            if distance.max() < 0.0001:
                break
            else:
                e_last = e.numpy()

    e_n = e.numpy()
    best = np.argmin(e_n)
    return param.numpy()[best], e_n[best]
