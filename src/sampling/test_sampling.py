from random import Random

from quantum_circuit import ALL_GATE_TYPES
from sampling import sample_by_gates, sample_by_layers
from test_helpers import SAMPLES_COUNT


def test_layerwise_sampling_has_gates_each_layer_without_collapse(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            circuit = sample_by_layers(5, 15, ALL_GATE_TYPES, random, False)
            for layer in circuit.gates:
                assert len(layer) > 0


def test_layerwise_sampling_has_gates_each_layer_with_collapse(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            circuit = sample_by_layers(5, 15, ALL_GATE_TYPES, random, True)
            for layer in circuit.gates:
                assert len(layer) > 0


def test_layerwise_sampling_has_correct_depth_without_collapse(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            target_depth = random.randrange(10, 30)
            circuit = sample_by_layers(5, target_depth, ALL_GATE_TYPES, random, False)
            assert len(circuit.gates) == target_depth


def test_layerwise_sampling_has_correct_depth_with_collapse(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            target_depth = random.randrange(10, 30)
            circuit = sample_by_layers(5, target_depth, ALL_GATE_TYPES, random, True)
            assert len(circuit.gates) == target_depth


def test_layerwise_sampling_has_no_overlapping_gates(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_layers(qubits, 15, ALL_GATE_TYPES, random, True)

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


def test_layerwise_sampling_does_fill_as_much_as_possible(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_layers(qubits, 15, ALL_GATE_TYPES, random, True)

            print(qubits)
            print(circuit.circ[0])

            odd_qubits = qubits % 2 != 0

            for layer in circuit.gates:
                seen = set()
                for gate in layer:
                    if not gate.type.is_single_qubit():
                        seen.add(gate.qubits[1])  # ty:ignore[index-out-of-bounds]
                    seen.add(gate.qubits[0])
                intersection = seen ^ {i for i in range(qubits)}
                free_count = len(intersection)
                assert (
                    free_count <= (1 if odd_qubits else 0)
                    # the layer is filled except for maybe two (in case of even qubits, one for odd)
                    or (
                        free_count
                        == qubits // 2  # the layer is half filled (even with odd total qubits)
                        or free_count == qubits // 2 + 1
                        if odd_qubits
                        else free_count == qubits // 2
                    )  # the layer is half filled (odd with odd total qubits)
                )


def test_layerwise_sampling_has_only_allowed_qubits(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_layers(qubits, 15, ALL_GATE_TYPES, random)

            print(qubits)
            print(circuit.circ[0])

            for layer in circuit.gates:
                for gate in layer:
                    if not gate.type.is_single_qubit():
                        assert gate.qubits[1] < qubits  # ty:ignore[index-out-of-bounds]
                    assert gate.qubits[0] < qubits


def test_gatewise_sampling_has_gates_each_layer(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            circuit = sample_by_gates(5, 15, ALL_GATE_TYPES, random)
            for layer in circuit.gates:
                assert len(layer) > 0


def test_gatewise_sampling_has_correct_depth(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            target_depth = random.randint(10, 30)
            circuit = sample_by_gates(5, target_depth, ALL_GATE_TYPES, random)
            assert len(circuit.gates) == target_depth


def test_gatewise_sampling_has_no_overlapping_gates(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_gates(qubits, 15, ALL_GATE_TYPES, random)

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


def test_gatewise_sampling_has_only_allowed_qubits(subtests):
    random = Random(1234)
    for samples in range(SAMPLES_COUNT):
        with subtests.test(i=samples):
            qubits = random.randrange(3, 10)
            circuit = sample_by_gates(qubits, 15, ALL_GATE_TYPES, random)

            print(qubits)
            print(circuit.circ[0])

            for layer in circuit.gates:
                for gate in layer:
                    if not gate.type.is_single_qubit():
                        assert gate.qubits[1] < qubits  # ty:ignore[index-out-of-bounds]
                    assert gate.qubits[0] < qubits
