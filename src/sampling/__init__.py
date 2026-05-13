from collections.abc import Callable
from functools import reduce
from random import Random

import qiskit
from qiskit.providers.backend import BackendV2
from qiskit.providers.fake_provider.generic_backend_v2 import GenericBackendV2
from qiskit_aer.noise.noise_model import NoiseModel

from hardware_descriptor import Topology
from quantum_circuit import GateType, ParametrizedQuantumCircuit, QuantumGate


def sample_by_layers(
    qubits: int,
    circuit_depth: int,
    max_params: int,
    gate_types: list[GateType],
    random: Random,
    collapse_non_overlapping: bool = True,
) -> ParametrizedQuantumCircuit:
    """
    Samples random quantum circuits using random gates created as half-layers.
    It works by choosing a random parity and gate type and creating a circuit layer from those gates

    Assumes that the qubits in the architecture are connected in a big loop, so it will connect
    q1 <-> q2 but not q2 <-> q4
    """

    pqc = ParametrizedQuantumCircuit(qubits)

    even_qubits = qubits % 2 == 0
    parameters = 0

    while len(pqc.gates) < circuit_depth and parameters < max_params:
        even_parity = random.random() < 0.5
        gate_type: GateType = random.choice(gate_types)
        if gate_type.is_single_qubit():
            positions = [(i,) for i in range(0 if even_parity else 1, qubits, 2)]
        else:
            direction = random.random() < 0.5
            positions = [
                (i, (i + 1) % qubits) if direction else ((i + 1) % qubits, i)
                for i in range(0 if even_parity else 1, (qubits if even_qubits else qubits - 1), 2)
            ]
        parameters += len(positions) * gate_type.is_parameterized()

        pqc.append_layer([QuantumGate(gate_type, pos) for pos in positions], collapse_non_overlapping)

    return pqc


def sample_by_gates(
    qubits: int, circuit_depth: int, max_params: int, gate_types: list[GateType], random: Random
) -> ParametrizedQuantumCircuit:
    pqc = ParametrizedQuantumCircuit(qubits)
    parameters = 0

    if qubits <= 1:  # can't have two-qubit gates
        gate_types = [ty for ty in gate_types if ty.is_single_qubit()]

    while len(pqc.gates) < circuit_depth and parameters < max_params:
        pos = random.randrange(0, qubits)
        gate_type = random.choice(gate_types)
        parameters += gate_type.is_parameterized()
        if gate_type.is_single_qubit():
            pqc.append_gate(QuantumGate(gate_type, (pos,)))
        else:
            direction = random.random() < 0.5
            pqc.append_gate(
                QuantumGate(gate_type, (pos, (pos + 1) % qubits) if direction else ((pos + 1) % qubits, pos))
            )

    return pqc


def sample_by_gates_fill(
    qubits: int,
    circuit_depth: int,
    max_params: int,
    gate_types: list[GateType],
    random: Random,
    hw_descriptor: Topology | None = None,
) -> ParametrizedQuantumCircuit:
    pqc = ParametrizedQuantumCircuit(qubits)
    parameters = 0

    single_gate_types: list[GateType] = [ty for ty in gate_types if ty.is_single_qubit()]
    if qubits <= 1:  # can't have two-qubit gates
        gate_types: list[GateType] = single_gate_types

    if hw_descriptor is None:
        hw_descriptor = Topology(
            GenericBackendV2(
                qubits,
                [gt.to_qiskit_str() for gt in gate_types],
                coupling_map=[t for x in range(qubits) for t in [[x, (x + 1) % qubits], [(x + 1) % qubits, x]]],
            )
        )

    while len(pqc.gates) < circuit_depth and parameters < max_params:
        if not one_positions:
            two_positions = list(hw_descriptor.graph.edges)
            one_positions = list(hw_descriptor.graph.nodes)

        gate_type = random.choice(gate_types if two_positions else single_gate_types)
        if gate_type.is_single_qubit():
            pos = (random.choice(one_positions),)
        else:
            pos = random.choice(two_positions)

        pqc.append_gate(QuantumGate(gate_type, pos))
        two_positions: list[tuple[int, int]] = [x for x in two_positions if (x[0] not in pos) and (x[1] not in pos)]
        one_positions: list[int] = [x for x in one_positions if x not in pos]

    return pqc


# ===========
# = Filters =
# ===========
# Filters wrap around existing sampling functions to add constraints


def ignore_too_many_two_qubit_gates(
    sampling_func: Callable[[Random], ParametrizedQuantumCircuit], max_two_qubit_prop: float = 0.5
) -> Callable[[Random], ParametrizedQuantumCircuit]:
    assert max_two_qubit_prop <= 1.0

    def filtered(random: Random):
        prop = 1.1

        while prop > max_two_qubit_prop:
            circ = sampling_func(random)
            total_gates = sum(len(layer) for layer in circ.gates)
            two_qubit_gates = sum(
                len([gate for gate in layer if not gate.type.is_single_qubit()]) for layer in circ.gates
            )
            prop = two_qubit_gates / total_gates

        return circ

    return filtered
