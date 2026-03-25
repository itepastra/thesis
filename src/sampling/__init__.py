from random import Random

from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


def sample_by_layers(
    qubits: int,
    circuit_depth: int,
    gate_types: list[QuantumType],
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

    while len(pqc.gates) < circuit_depth:
        even_parity = random.random() < 0.5
        gate_type: QuantumType = random.choice(gate_types)
        if gate_type.is_single_qubit():
            positions = [(i,) for i in range(0 if even_parity else 1, qubits, 2)]
        else:
            direction = random.random() < 0.5
            positions = [
                (i, (i + 1) % qubits) if direction else ((i + 1) % qubits, i)
                for i in range(0 if even_parity else 1, qubits, 2)
            ]

        pqc.append_layer(
            [QuantumGate(gate_type, pos) for pos in positions], collapse_non_overlapping
        )

    return pqc


def sample_by_gates(
    qubits: int, circuit_depth: int, gate_types: list[QuantumType], random: Random
) -> ParametrizedQuantumCircuit:
    pqc = ParametrizedQuantumCircuit(qubits)

    while len(pqc.gates) < circuit_depth:
        pos = random.randrange(0, qubits)
        gate_type = random.choice(gate_types)
        if gate_type.is_single_qubit():
            pqc.append_gate(QuantumGate(gate_type, (pos,)))
        else:
            direction = random.random() < 0.5
            pqc.append_gate(
                QuantumGate(
                    gate_type, (pos, (pos + 1) % qubits) if direction else ((pos + 1) % qubits, pos)
                )
            )

    return pqc
