from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
import tensorcircuit as tc

from quantum_circuit import GateType, ParametrizedQuantumCircuit, QuantumGate


def build_tensor_circuit_factory(
    circ: ParametrizedQuantumCircuit, prepend_gates: list[QuantumGate], hamiltonian
) -> Callable[..., tc.Circuit]:
    def tensor_circuit_measurement(param):
        tcirc = tc.Circuit(circ.qubits)
        paramc = tc.backend.cast(param, tc.dtypestr)
        current_param_index = 0
        to_add = prepend_gates + [gate for layer in circ.gates for gate in layer]
        for gate in to_add:
            if gate.type == GateType.Hadamard:
                tcirc.h(gate.qubits[0])
            elif gate.type == GateType.X:
                tcirc.x(gate.qubits[0])
            elif gate.type == GateType.RX:
                tcirc.rx(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == GateType.RXX:
                tcirc.rxx(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == GateType.Y:
                tcirc.y(gate.qubits[0])
            elif gate.type == GateType.RY:
                tcirc.ry(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == GateType.RYY:
                tcirc.ryy(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == GateType.Z:
                tcirc.z(gate.qubits[0])
            elif gate.type == GateType.RZ:
                tcirc.rz(gate.qubits[0], theta=paramc[current_param_index])
            elif gate.type == GateType.RZZ:
                tcirc.rzz(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == GateType.XX:
                tcirc.rxx(gate.qubits[0], gate.qubits[1], theta=np.pi / 2.0)  # ty:ignore[index-out-of-bounds]
            elif gate.type == GateType.YY:
                tcirc.ryy(gate.qubits[0], gate.qubits[1], theta=np.pi / 2.0)  # ty:ignore[index-out-of-bounds]
            elif gate.type == GateType.ZZ:
                tcirc.rzz(gate.qubits[0], gate.qubits[1], theta=np.pi / 2.0)  # ty:ignore[index-out-of-bounds]
            elif gate.type == GateType.CRX:
                tcirc.crx(
                    gate.qubits[0], gate.qubits[1], theta=paramc[current_param_index]  # ty:ignore[index-out-of-bounds]
                )
            elif gate.type == GateType.CX:
                tcirc.cx(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            elif gate.type == GateType.CZ:
                tcirc.cz(gate.qubits[0], gate.qubits[1])  # ty:ignore[index-out-of-bounds]
            else:
                raise NotImplementedError(f"Gate type {gate.type} not implemented")

            current_param_index += gate.type.is_parameterized()
        expectation = tc.templates.measurements.operator_expectation(tcirc, hamiltonian)
        return expectation

    return tensor_circuit_measurement
