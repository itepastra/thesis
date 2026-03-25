from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from qiskit import transpile
from qiskit_aer.backends.aer_simulator import AerSimulator
from qiskit_aer.backends.aerbackend import AerBackend
from scipy import stats
from tqdm import tqdm

if TYPE_CHECKING:
    from quantum_circuit import ParametrizedQuantumCircuit
    from quantum_circuit.proxy_config import ProxyConfig


def single_circuit_param_fidelity(
    circ: ParametrizedQuantumCircuit, samples: int, backend: AerBackend
) -> float:
    qc, thetas = circ.circ
    qc.save_statevector()

    tqc = transpile(qc, backend)

    number_of_initial_circuits = 2 * samples

    params: NDArray[np.float64] = np.random.uniform(
        -np.pi, np.pi, (len(thetas), number_of_initial_circuits)
    )

    binds = [{param: params[idx] for idx, param in enumerate(thetas.params)}]

    job = backend.run([tqc], parameter_binds=binds)
    result = job.result()

    sv = np.array(
        [
            np.asarray(result.get_statevector(i), dtype=np.complex128)
            for i in range(number_of_initial_circuits)
        ]
    )
    left = sv[:samples]
    right = sv[samples:]

    ret = np.power(np.absolute((left * right.conjugate()).sum(-1)), 2)

    return ret


def calculate_fidelity(
    circs: list[ParametrizedQuantumCircuit] | ParametrizedQuantumCircuit, config: ProxyConfig
) -> NDArray[np.float64]:
    from quantum_circuit import ParametrizedQuantumCircuit

    if isinstance(circs, ParametrizedQuantumCircuit):
        circs = [circs]
    raise NotImplementedError


def calculate_expressivity(
    circs: list[ParametrizedQuantumCircuit] | ParametrizedQuantumCircuit, config: ProxyConfig
) -> NDArray[np.float64]:
    tqdm_depth = 1
    from quantum_circuit import ParametrizedQuantumCircuit

    if isinstance(circs, ParametrizedQuantumCircuit):
        circs = [circs]

    qubits = config.qubits
    samples = config.expressivity_samples
    bin_count = config.expressivity_bins
    force_recalculate = config.force_recalculate
    bins: np.ndarray[tuple[int], np.dtype[np.float64]] = np.linspace(0.0, 1.0, bin_count + 1)

    haar_power = (1 << qubits) - 1
    lower_edges: np.ndarray[tuple[int], np.dtype[np.float64]] = -1.0 * np.power(
        1.0 - bins[:-1], haar_power
    )
    higher_edges: np.ndarray[tuple[int], np.dtype[np.float64]] = -1.0 * np.power(
        1.0 - bins[1:], haar_power
    )
    haar_values: np.ndarray[tuple[int], np.dtype[np.float64]] = higher_edges - lower_edges

    backend = AerSimulator(method="statevector")

    fidelities = np.zeros((len(circs), config.expressivity_samples))
    for idx, circuit in tqdm(
        enumerate(circs),
        total=len(circs),
        position=tqdm_depth,
        desc="Computing Fidelities",
        leave=False,
    ):
        if not force_recalculate and circs[idx]._expressivity is not None:
            continue
        fidelities[idx] = single_circuit_param_fidelity(circuit, samples, backend)

    expressivity = np.zeros((len(circs)))
    for idx, fid in tqdm(
        enumerate(fidelities),
        total=len(circs),
        position=tqdm_depth,
        desc="Computing Expressibility",
        leave=False,
    ):
        if not force_recalculate and circs[idx]._expressivity is not None:
            continue
        bin_idx = np.floor(fid * bin_count).astype(int)
        num = np.array([len(bin_idx[bin_idx == i]) for i in range(bin_count)])

        expressivity[idx] = -stats.entropy(num, haar_values)
        # NOTE: I'm setting the expressivity here directly, for caching
        circs[idx]._expressivity = float(expressivity[idx])

    return expressivity


def calculate_entanglement(
    circs: list[ParametrizedQuantumCircuit] | ParametrizedQuantumCircuit, config: ProxyConfig
) -> NDArray[np.float64]:
    if isinstance(circs, ParametrizedQuantumCircuit):
        circs = [circs]
    raise NotImplementedError
