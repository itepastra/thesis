from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.parameter import Parameter
from qiskit.circuit.parametertable import ParameterView
from qiskit.circuit.parametervector import ParameterVector

if TYPE_CHECKING:
    from quantum_circuit import GateType, ParametrizedQuantumCircuit, QuantumGate


def add_qubit_gate(circ: QuantumCircuit, gate: QuantumGate, thetas: ParameterVector, current_theta_index: int) -> int:
    from quantum_circuit import GateType

    match gate.type:
        case GateType.Identity:
            circ.id(gate.qubits[0])
        case GateType.Hadamard:
            circ.h(gate.qubits[0])
        case GateType.X:
            circ.x(gate.qubits[0])
        case GateType.RX:
            circ.rx(thetas[current_theta_index], gate.qubits[0])
        case GateType.RXX:
            circ.rxx(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.Y:
            circ.y(gate.qubits[0])
        case GateType.RY:
            circ.ry(thetas[current_theta_index], gate.qubits[0])
        case GateType.RYY:
            circ.ryy(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.Z:
            circ.z(gate.qubits[0])
        case GateType.RZ:
            circ.rz(thetas[current_theta_index], gate.qubits[0])
        case GateType.RZZ:
            circ.rzz(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.XX:
            circ.rxx(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.YY:
            circ.ryy(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.ZZ:
            circ.rzz(np.pi, gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.CRX:
            circ.crx(thetas[current_theta_index], gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.CX:
            circ.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
        case GateType.CZ:
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
            except Exception as e:
                print(e)
                print(
                    f"tried adding {gate} to \n\n{circ}\n\nWith theta index {current_theta_index} (len is {len(thetas)}, the pqc had gates \n{'\n'.join(str(x) for x in pqc.gates)}"
                )
                raise Exception

    circ.save_statevector()
    return circ, thetas
