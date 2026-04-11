from random import Random

import sampling
from quantum_circuit import ALL_GATE_TYPES, ParametrizedQuantumCircuit, QuantumGate, QuantumType
from test_helpers import SAMPLES_COUNT


def test_append_gate_collapses_when_last_layer_empty():
    circ = ParametrizedQuantumCircuit(2)
    assert len(circ.gates) == 0
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    assert len(circ.gates) == 1
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (1,)))
    assert len(circ.gates) == 1


def test_append_gate_makes_new_layer_when_last_layer_full():
    circ = ParametrizedQuantumCircuit(2)
    assert len(circ.gates) == 0
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    assert len(circ.gates) == 1
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    assert len(circ.gates) == 2


def test_append_gate_puts_gate_at_first_valid_spot():
    circ = ParametrizedQuantumCircuit(2)
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    circ.append_gate(QuantumGate(QuantumType.CX, (0, 1)))
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    circ.append_gate(QuantumGate(QuantumType.Identity, (1,)))

    assert QuantumGate(QuantumType.Identity, (1,)) in (circ.gates[2])


def test_append_gate_does_not_change_existing_gates():
    circ = ParametrizedQuantumCircuit(2)
    circ.append_gate(QuantumGate(QuantumType.RX, (0,)))
    gates_a = [[g for g in layer] for layer in circ.gates]
    circ.append_gate(QuantumGate(QuantumType.CX, (0, 1)))
    assert all(gate in layer for original, layer in zip(gates_a, circ.gates) for gate in original)
    gates_b = [[g for g in layer] for layer in circ.gates]
    circ.append_gate(QuantumGate(QuantumType.RY, (0,)))
    assert all(gate in layer for original, layer in zip(gates_b, circ.gates) for gate in original)
    gates_c = [[g for g in layer] for layer in circ.gates]
    circ.append_gate(QuantumGate(QuantumType.RZ, (0,)))
    assert all(gate in layer for original, layer in zip(gates_c, circ.gates) for gate in original)
    gates_d = [[g for g in layer] for layer in circ.gates]
    circ.append_gate(QuantumGate(QuantumType.Identity, (1,)))
    assert all(gate in layer for original, layer in zip(gates_d, circ.gates) for gate in original)


def test_append_single_qubit_gate_updates_qubit_mask_correctly():
    circ = ParametrizedQuantumCircuit(4)
    circ.append_gate(QuantumGate(QuantumType.Hadamard, (0,)))
    assert len(circ.layer_bitsets) == 1
    assert circ.layer_bitsets[0] == 0b0001
    circ.append_gate(QuantumGate(QuantumType.Identity, (1,)))
    assert len(circ.layer_bitsets) == 1
    assert circ.layer_bitsets[0] == 0b0011
    circ.append_gate(QuantumGate(QuantumType.RX, (3,)))
    assert len(circ.layer_bitsets) == 1
    assert circ.layer_bitsets[0] == 0b1011
    circ.append_gate(QuantumGate(QuantumType.RY, (1,)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b1011
    assert circ.layer_bitsets[1] == 0b0010
    circ.append_gate(QuantumGate(QuantumType.RZ, (3,)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b1011
    assert circ.layer_bitsets[1] == 0b1010
    circ.append_gate(QuantumGate(QuantumType.X, (2,)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b1111
    assert circ.layer_bitsets[1] == 0b1010
    circ.append_gate(QuantumGate(QuantumType.Y, (2,)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b1111
    assert circ.layer_bitsets[1] == 0b1110
    circ.append_gate(QuantumGate(QuantumType.Z, (3,)))
    assert len(circ.layer_bitsets) == 3
    assert circ.layer_bitsets[0] == 0b1111
    assert circ.layer_bitsets[1] == 0b1110
    assert circ.layer_bitsets[2] == 0b1000


def test_append_two_qubit_gate_updates_qubit_mask_correctly():
    circ = ParametrizedQuantumCircuit(4)
    circ.append_gate(QuantumGate(QuantumType.CX, (1, 2)))
    assert len(circ.layer_bitsets) == 1
    assert circ.layer_bitsets[0] == 0b0110
    circ.append_gate(QuantumGate(QuantumType.CZ, (2, 3)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b0110
    assert circ.layer_bitsets[1] == 0b1100
    circ.append_gate(QuantumGate(QuantumType.CRX, (0, 1)))
    assert len(circ.layer_bitsets) == 2
    assert circ.layer_bitsets[0] == 0b0110
    assert circ.layer_bitsets[1] == 0b1111
    circ.append_gate(QuantumGate(QuantumType.RXX, (0, 3)))
    assert len(circ.layer_bitsets) == 3
    assert circ.layer_bitsets[0] == 0b0110
    assert circ.layer_bitsets[1] == 0b1111
    assert circ.layer_bitsets[2] == 0b1001
    circ.append_gate(QuantumGate(QuantumType.RYY, (0, 3)))
    assert len(circ.layer_bitsets) == 4
    assert circ.layer_bitsets[0] == 0b0110
    assert circ.layer_bitsets[1] == 0b1111
    assert circ.layer_bitsets[2] == 0b1001
    assert circ.layer_bitsets[3] == 0b1001
    circ.append_gate(QuantumGate(QuantumType.RZZ, (1, 2)))
    assert len(circ.layer_bitsets) == 4
    assert circ.layer_bitsets[0] == 0b0110
    assert circ.layer_bitsets[1] == 0b1111
    assert circ.layer_bitsets[2] == 0b1111
    assert circ.layer_bitsets[3] == 0b1001


def qubit_mask_stays_in_sync_with_append_gate(subtests):
    circ = ParametrizedQuantumCircuit(5)
    random = Random(1234)
    # generate a very deep circuit
    for _ in range(10000):
        choice = random.choice(ALL_GATE_TYPES)
        if choice.is_single_qubit():
            circ.append_gate(QuantumGate(choice, (random.randrange(0, 5),)))
        else:
            qubits = random.sample([0, 1, 2, 3, 4], 2)
            circ.append_gate(QuantumGate(choice, (qubits[0], qubits[1])))
        assert len(circ.gates) == len(circ.layer_bitsets)

    n = 0
    for layer, bits in zip(circ.gates, circ.layer_bitsets, strict=True):
        with subtests.test(i=n):
            for gate in layer:
                for qubit in gate.qubits:
                    assert 1 << qubit in bits
        n += 1
