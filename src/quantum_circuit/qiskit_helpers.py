from typing import TYPE_CHECKING

from qiskit import QuantumCircuit
from qiskit.circuit.parameter import Parameter
from qiskit.circuit.parametervector import ParameterVector

if TYPE_CHECKING:
    from quantum_circuit import (ParametrizedQuantumCircuit, QuantumGate,
                                 QuantumType)


def add_qubit_gate(circ: QuantumCircuit, gate: QuantumGate, theta: Parameter) -> int:
    match gate.type:
        case QuantumType.Identity:
            return 0
        case QuantumType.Hadamard:
            circ.h(gate.qubits[0])
            return 0
        case QuantumType.X:
            circ.x(gate.qubits[0])
            return 0
        case QuantumType.RX:
            circ.rx(theta, gate.qubits[0])
            return 1
        case QuantumType.RXX:
            circ.rxx(theta, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            return 1
        case QuantumType.Y:
            circ.y(gate.qubits[0])
            return 0
        case QuantumType.RY:
            circ.ry(theta, gate.qubits[0])
            return 1
        case QuantumType.RYY:
            circ.ryy(theta, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            return 1
        case QuantumType.Z:
            circ.z(gate.qubits[0])
            return 0
        case QuantumType.RZ:
            circ.rz(theta, gate.qubits[0])
            return 1
        case QuantumType.RZZ:
            circ.rzz(theta, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            return 1
        case QuantumType.CRX:
            circ.crx(theta, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            return 1
        case QuantumType.CX:
            circ.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            return 0
    raise NotImplementedError


def build_qiskit_circ(pqc: "ParametrizedQuantumCircuit") -> tuple[QuantumCircuit, ParameterVector]:

    circ = QuantumCircuit(pqc.qubits)
    thetas = ParameterVector("thetas", circ.parameters)

    current_theta_index = 0
    for layer in pqc.gates:
        for gate in layer:
            current_theta_index += add_qubit_gate(circ, gate, thetas[current_theta_index])

    return circ, thetas
