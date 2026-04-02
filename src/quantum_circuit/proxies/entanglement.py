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


def calculate_entanglement(
    circs: list[ParametrizedQuantumCircuit] | ParametrizedQuantumCircuit, config: ProxyConfig
) -> NDArray[np.float64]:
    if isinstance(circs, ParametrizedQuantumCircuit):
        circs = [circs]
    raise NotImplementedError
