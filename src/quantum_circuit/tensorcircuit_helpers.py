from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import tensorcircuit as tc

if TYPE_CHECKING:
    from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


def build_tensor_circuit(circ: ParametrizedQuantumCircuit) -> Callable[..., tc.Circuit]:
    def tfim(param):
        c = tc.Circuit(circ.qubits)
        paramc = tc.backend.cast(param, tc.dtypestr)
        current_param_index = 0
        for layer in circ.gates:
            for gate in layer:
                match gate.type:
                    case QuantumType.Identity:
                        pass
                    case QuantumType.Hadamard:
                        c.H(gate.qubits[0])
                    case QuantumType.X:
                        c.X(gate.qubits[0])
                    case QuantumType.RX:
                        c.rx(gate.qubits[0], theta=paramc[current_param_index])
                    case QuantumType.RXX:
                        c.rxx(
                            gate.qubits[0],
                            gate.qubits[1],  # ty:ignore[index-out-of-bounds]
                            theta=paramc[current_param_index],
                        )
                    case QuantumType.Y:
                        c.Y(gate.qubits[0])
                    case QuantumType.RY:
                        c.ry(gate.qubits[0], theta=paramc[current_param_index])
                    case QuantumType.RYY:
                        c.ryy(
                            gate.qubits[0],
                            gate.qubits[1],  # ty:ignore[index-out-of-bounds]
                            theta=paramc[current_param_index],
                        )
                    case QuantumType.Z:
                        c.Z(gate.qubits[0])
                    case QuantumType.RZ:
                        c.rz(gate.qubits[0], theta=paramc[current_param_index])
                    case QuantumType.RZZ:
                        c.rzz(
                            gate.qubits[0],
                            gate.qubits[1],  # ty:ignore[index-out-of-bounds]
                            theta=paramc[current_param_index],
                        )
                    case QuantumType.CRX:
                        c.crx(
                            gate.qubits[0],
                            gate.qubits[1],  # ty:ignore[index-out-of-bounds]
                            theta=paramc[current_param_index],
                        )
                    case QuantumType.CX:
                        c.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
                    case QuantumType.CZ:
                        c.cz(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
                    case _:
                        raise NotImplementedError(f"Gate type {gate.type} not implemented")
                current_param_index += gate.type.is_parameterized()

        return c

    return tfim
