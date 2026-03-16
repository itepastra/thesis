from typing import TYPE_CHECKING

from qiskit import QuantumCircuit
from qiskit.circuit.parametervector import ParameterVector

if TYPE_CHECKING:
    from quantum_circuit import ParametrizedQuantumCircuit


def build_qiskit_circ(pqc: "ParametrizedQuantumCircuit") -> tuple[QuantumCircuit, ParameterVector]:
    raise NotImplementedError
