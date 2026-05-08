import math
from random import Random

import numpy as np
import pytest
from scipy import stats

from quantum_circuit import ALL_GATE_TYPES, ParametrizedQuantumCircuit, QuantumGate, QuantumType
from quantum_circuit.proxies.path import paths_proxy
from quantum_circuit.proxy_config import ProxyConfig
from sampling import sample_by_gates, sample_by_layers
from test_helpers import SAMPLES_COUNT


def test_identity_circuit_has_correct_expressivity(subtests):
    for qubits in range(1, 10):
        with subtests.test(f"qubits: {qubits}"):
            circ = ParametrizedQuantumCircuit(qubits)
            circ.append_layer([QuantumGate(QuantumType.Identity, (qb,)) for qb in range(qubits)], True)

            proxy_config = ProxyConfig(qubits, expressivity_bins=75, random=Random(1337))
            target_expressivity = ((2**qubits) - 1) * math.log(proxy_config.expressivity_bins)

            assert circ.expressivity(proxy_config) == pytest.approx(target_expressivity)


def test_rz_circuit_has_correct_expressivity(subtests):
    qubits = 1
    proxy_config = ProxyConfig(
        qubits, expressivity_bins=75, expressivity_samples=5000, force_recalculate=True, random=Random(1337)
    )
    circ = ParametrizedQuantumCircuit(qubits)
    circ.append_gate(QuantumGate(QuantumType.RZ, (0,)))

    # RZ |0> = |0> so it should give the same result as the identity circuit
    exact_result = ((2**qubits) - 1) * math.log(proxy_config.expressivity_bins)

    for attempt in range(SAMPLES_COUNT):
        with subtests.test(attempt):
            print(f"attempt: {attempt} failed")
            # accept some uncertainty around the exact value, since we are approximating the expressivity.
            # might be better to test if the distribution of N attempts aligns with the exact_result
            assert circ.expressivity(proxy_config) == pytest.approx(exact_result)


def test_rx_circuit_has_correct_expressivity(subtests):
    qubits = 1
    proxy_config = ProxyConfig(
        qubits, expressivity_bins=75, expressivity_samples=100000, force_recalculate=True, random=Random(1337)
    )

    haar_power = 2**1 - 1
    bins: np.ndarray[tuple[int], np.dtype[np.float64]] = np.linspace(0.0, 1.0, proxy_config.expressivity_bins + 1)

    lower = -np.power(1 - bins[:-1], haar_power)
    upper = -np.power(1 - bins[1:], haar_power)
    haar_values = upper - lower

    exact_result = stats.entropy(
        2 / np.pi * (np.arccos(np.sqrt(bins[1:])) - np.arccos(np.sqrt(bins[:-1]))), haar_values
    )

    circ = ParametrizedQuantumCircuit(qubits)
    circ.append_gate(QuantumGate(QuantumType.RX, (0,)))

    for attempt in range(SAMPLES_COUNT):
        with subtests.test(attempt):
            print(f"attempt: {attempt} failed")
            # accept some uncertainty around the exact value, since we are approximating the expressivity.
            # might be better to test if the distribution of N attempts aligns with the exact_result
            assert circ.expressivity(proxy_config) == pytest.approx(exact_result, 0.01)


def test_simple_chain_circuit_has_correct_expressivity(subtests):
    qubits = 1
    # increase the sample count to make the approximation closer
    proxy_config = ProxyConfig(
        qubits, expressivity_bins=75, expressivity_samples=100000, force_recalculate=True, random=Random(1337)
    )

    exact_result = 0.011116

    circ = ParametrizedQuantumCircuit(qubits)
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    circ.append_gate(QuantumGate(QuantumType.RZ, (0,)))
    circ.append_gate(QuantumGate(QuantumType.RX, (0,)))

    for attempt in range(SAMPLES_COUNT):
        with subtests.test(attempt):
            assert circ.expressivity(proxy_config) == pytest.approx(exact_result, 0.01)


NON_PARAMETRIZED_GATES = [
    QuantumType.Identity,
    QuantumType.Hadamard,
    QuantumType.X,
    QuantumType.Y,
    QuantumType.Z,
    QuantumType.CX,
    QuantumType.XX,
    QuantumType.YY,
    QuantumType.ZZ,
]


def test_non_parameterized_circuits_have_correct_expressivity(subtests):
    random = Random(1337)
    lower = 1
    upper = 10
    for qubits in range(lower, upper):
        for sample in range(SAMPLES_COUNT // (upper - lower)):
            with subtests.test(f"qubits: {qubits}, sample {sample}"):
                circ = sample_by_gates(qubits, 15, 900, NON_PARAMETRIZED_GATES, random)

                proxy_config = ProxyConfig(qubits, expressivity_bins=75, random=random)
                target_expressivity = ((2**qubits) - 1) * math.log(proxy_config.expressivity_bins)

                assert circ.expressivity(proxy_config) == pytest.approx(target_expressivity)
