from random import Random

from quantum_circuit import ALL_GATE_TYPES
from sampling import sample_by_gates
from test_helpers import SAMPLES_COUNT


def test_gatewise_sampling_has_gates_each_layer(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            circuit = sample_by_gates(5, 15, 900, ALL_GATE_TYPES, random)
            for layer in circuit.gates:
                assert len(layer) > 0


def test_gatewise_sampling_has_correct_depth(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            target_depth = random.randint(10, 30)
            circuit = sample_by_gates(5, target_depth, 900, ALL_GATE_TYPES, random)
            assert len(circuit.gates) == target_depth


def test_gatewise_sampling_has_no_overlapping_gates(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_gates(qubits, 15, 900, ALL_GATE_TYPES, random)

            print(qubits)
            print(circuit.circ[0])

            for layer in circuit.gates:
                seen = set()
                for gate in layer:
                    if not gate.type.is_single_qubit():
                        assert gate.qubits[1] not in seen  # ty:ignore[index-out-of-bounds]
                        seen.add(gate.qubits[1])  # ty:ignore[index-out-of-bounds]
                    assert gate.qubits[0] not in seen
                    seen.add(gate.qubits[0])


def test_gatewise_sampling_does_not_add_two_qubit_gates_on_one_qubit_circuits(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            circuit = sample_by_gates(1, 15, 900, ALL_GATE_TYPES, random)

            for layer in circuit.gates:
                for gate in layer:
                    assert gate.type.is_single_qubit()


def test_gatewise_sampling_has_only_allowed_qubits(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_gates(qubits, 15, 900, ALL_GATE_TYPES, random)

            print(qubits)
            print(circuit.circ[0])

            for layer in circuit.gates:
                for gate in layer:
                    if not gate.type.is_single_qubit():
                        assert gate.qubits[1] < qubits  # ty:ignore[index-out-of-bounds]
                    assert gate.qubits[0] < qubits
