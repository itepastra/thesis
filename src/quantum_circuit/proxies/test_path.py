from random import Random

from quantum_circuit import ALL_GATE_TYPES, GateType, ParametrizedQuantumCircuit, QuantumGate
from quantum_circuit.proxies.path import paths_proxy
from sampling import sample_by_layers
from test_helpers import SAMPLES_COUNT


def test_path_proxy_counts_paths_correctly_for_simple_circuits(subtests):
    with subtests.test("2 qubits, 1 cnot"):
        circ = ParametrizedQuantumCircuit(2)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        # 0 ----C----
        # 1 ----X----
        # 1. 0 -> 0
        # 2. 0 -> 1
        # 3. 1 -> 0
        # 4. 1 -> 1

        path_count = paths_proxy([circ])
        assert path_count[0] == 4
    with subtests.test("2 qubits, 2 cnot"):
        circ = ParametrizedQuantumCircuit(2)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        # 0 ----C----C----
        # 1 ----X----X----
        # 1. 0 -> 0 -> 0
        # 2. 0 -> 1 -> 0
        # 3. 1 -> 0 -> 0
        # 4. 1 -> 1 -> 0
        # 5. 0 -> 0 -> 1
        # 6. 0 -> 1 -> 1
        # 7. 1 -> 0 -> 1
        # 8. 1 -> 1 -> 1

        path_count = paths_proxy([circ])
        assert path_count[0] == 8

    with subtests.test("3 qubits, 1 cnot"):
        circ = ParametrizedQuantumCircuit(3)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        # 0 ----C----
        # 1 ----X----
        # 2 ---------
        # 1. 0 -> 0
        # 2. 0 -> 1
        # 3. 1 -> 0
        # 4. 1 -> 1
        # 5. 2 -> 2

        path_count = paths_proxy([circ])
        assert path_count[0] == 5

    with subtests.test("3 qubits, 2 cnot"):
        circ = ParametrizedQuantumCircuit(3)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        circ.append_layer([QuantumGate(GateType.CX, (1, 2))], False)
        # 0 ----C---------
        # 1 ----X----C----
        # 2 ---------X----
        # 1. 0 -> 0 -> 0
        # 2. 0 -> 1 -> 1
        # 3. 0 -> 1 -> 2
        # 4. 1 -> 0 -> 0
        # 5. 1 -> 1 -> 1
        # 6. 1 -> 1 -> 2
        # 7. 2 -> 2 -> 1
        # 8. 2 -> 2 -> 2

        path_count = paths_proxy([circ])
        assert path_count[0] == 8

    with subtests.test("3 qubits, 3 cnot 010"):
        circ = ParametrizedQuantumCircuit(3)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        circ.append_layer([QuantumGate(GateType.CX, (1, 2))], False)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        #  0 ----C---------C----
        #  1 ----X----C----X----
        #  2 ---------X---------
        #  1. 0 -> 0 -> 0 -> 0
        #  2. 0 -> 0 -> 0 -> 1
        #  3. 0 -> 1 -> 1 -> 0
        #  4. 0 -> 1 -> 1 -> 1
        #  5. 0 -> 1 -> 2 -> 2
        #  6. 1 -> 0 -> 0 -> 0
        #  7. 1 -> 0 -> 0 -> 1
        #  8. 1 -> 1 -> 1 -> 0
        #  9. 1 -> 1 -> 1 -> 1
        # 10. 1 -> 1 -> 2 -> 2
        # 11. 2 -> 2 -> 1 -> 0
        # 12. 2 -> 2 -> 1 -> 1
        # 13. 2 -> 2 -> 2 -> 2

        path_count = paths_proxy([circ])
        assert path_count[0] == 13

    with subtests.test("3 qubits, 3 cnot 011"):
        circ = ParametrizedQuantumCircuit(3)
        circ.append_layer([QuantumGate(GateType.CX, (0, 1))], False)
        circ.append_layer([QuantumGate(GateType.CX, (1, 2))], False)
        circ.append_layer([QuantumGate(GateType.CX, (1, 2))], False)
        #  0 ----C--------------
        #  1 ----X----C----C----
        #  2 ---------X----X----
        #  1. 0 -> 0 -> 0 -> 0
        #  2. 0 -> 1 -> 1 -> 1
        #  3. 0 -> 1 -> 1 -> 2
        #  4. 0 -> 1 -> 2 -> 1
        #  5. 0 -> 1 -> 2 -> 2
        #  6. 1 -> 0 -> 0 -> 0
        #  7. 1 -> 1 -> 1 -> 1
        #  8. 1 -> 1 -> 1 -> 2
        #  9. 1 -> 1 -> 2 -> 1
        # 10. 1 -> 1 -> 2 -> 2
        # 11. 2 -> 2 -> 1 -> 1
        # 12. 2 -> 2 -> 1 -> 2
        # 13. 2 -> 2 -> 2 -> 1
        # 14. 2 -> 2 -> 2 -> 2

        path_count = paths_proxy([circ])
        assert path_count[0] == 14


def test_path_proxy_does_not_depend_on_single_qubit_gates(subtests):
    random = Random(1234)
    gateset = [typ for typ in ALL_GATE_TYPES if typ.is_single_qubit()]
    for i in range(SAMPLES_COUNT):
        with subtests.test(i=i):
            qubits = random.randrange(1, 11)
            circs = [sample_by_layers(qubits, 10, 900, gateset, random, True)]
            path_counts = paths_proxy(circs)
            assert path_counts[0] == qubits


def test_path_proxy_returns_same_length_as_inputs(subtests):
    random = Random(1234)
    for i in range(SAMPLES_COUNT):
        with subtests.test(i=i):
            count = random.randrange(1, 100)
            qubits = random.randrange(1, 11)
            circs = [sample_by_layers(qubits, 10, 900, ALL_GATE_TYPES, random, True) for _ in range(count)]
            path_counts = paths_proxy(circs)
            assert len(path_counts) == len(circs)
