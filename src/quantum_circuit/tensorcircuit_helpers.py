from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import tensorcircuit as tc

from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


def build_tensor_circuit_factory(
    circ: ParametrizedQuantumCircuit, prepend_gates: list[QuantumGate], hamiltonian
) -> Callable[..., tc.Circuit]:
    def tensor_circuit_measurement(param):
        tcirc = tc.Circuit(circ.qubits)
        paramc = tc.backend.cast(param, tc.dtypestr)
        current_param_index = 0
        to_add = prepend_gates + [gate for layer in circ.gates for gate in layer]
        for gate in to_add:
            if gate.type == QuantumType.Hadamard:
                tcirc.h(gate.qubits[0])
            elif gate.type == QuantumType.X:
                tcirc.x(gate.qubits[0])
            elif gate.type == QuantumType.RX:
                tcirc.rx(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == QuantumType.RXX:
                tcirc.rxx(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == QuantumType.Y:
                tcirc.y(gate.qubits[0])
            elif gate.type == QuantumType.RY:
                tcirc.ry(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == QuantumType.RYY:
                tcirc.ryy(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == QuantumType.Z:
                tcirc.z(gate.qubits[0])
            elif gate.type == QuantumType.RZ:
                tcirc.rz(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == QuantumType.RZZ:
                tcirc.rzz(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == QuantumType.CRX:
                tcirc.crx(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == QuantumType.CX:
                tcirc.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            elif gate.type == QuantumType.CZ:
                tcirc.cz(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            else:
                raise NotImplementedError(f"Gate type {gate.type} not implemented")

            current_param_index += gate.type.is_parameterized()
        expectation = tc.templates.measurements.operator_expectation(tcirc, hamiltonian)
        return expectation

    return tensor_circuit_measurement
