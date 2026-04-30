from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.parameter import Parameter
from qiskit.circuit.parametertable import ParameterView
from qiskit.circuit.parametervector import ParameterVector

if TYPE_CHECKING:
    from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


def add_qubit_gate(circ: QuantumCircuit, gate: QuantumGate, thetas: ParameterVector, current_theta_index: int) -> int:
    from quantum_circuit import QuantumType

    match gate.type:
        case QuantumType.Identity:
            circ.id(gate.qubits[0])
        case QuantumType.Hadamard:
            circ.h(gate.qubits[0])
        case QuantumType.X:
            circ.x(gate.qubits[0])
        case QuantumType.RX:
            circ.rx(thetas[current_theta_index], gate.qubits[0])
        case QuantumType.RXX:
            circ.rxx(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.Y:
            circ.y(gate.qubits[0])
        case QuantumType.RY:
            circ.ry(thetas[current_theta_index], gate.qubits[0])
        case QuantumType.RYY:
            circ.ryy(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.Z:
            circ.z(gate.qubits[0])
        case QuantumType.RZ:
            circ.rz(thetas[current_theta_index], gate.qubits[0])
        case QuantumType.RZZ:
            circ.rzz(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.XX:
            circ.rxx(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.YY:
            circ.ryy(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.ZZ:
            circ.rzz(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.CRX:
            circ.crx(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.CX:
            circ.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case QuantumType.CZ:
            circ.cz(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case _:
            raise NotImplementedError(f"Gate type {gate.type} not implemented")
    return gate.type.is_parameterized()


def build_qiskit_circ(pqc: "ParametrizedQuantumCircuit") -> tuple[QuantumCircuit, ParameterVector]:

    circ = QuantumCircuit(pqc.qubits)
    pqc.check_parameters(False)
    thetas = ParameterVector("thetas", pqc.parameters)

    current_theta_index = 0
    for layer in pqc.gates:
        for gate in layer:
            try:
                current_theta_index += add_qubit_gate(circ, gate, thetas, current_theta_index)
            except:
                print(
                    f"tried adding {gate} to \n\n{circ}\n\nWith theta index {current_theta_index} (len is {len(thetas)}, the pqc had gates \n{'\n'.join(str(x) for x in pqc.gates)}"
                )
                raise Exception

    return circ, thetas
