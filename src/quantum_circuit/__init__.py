import enum
from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit.circuit.parametervector import ParameterVector

from quantum_circuit.proxy_config import ProxyConfig
from quantum_circuit.qiskit_helpers import build_qiskit_circ

from .proxies import (calculate_entanglement, calculate_expressivity,
                      calculate_fidelity)


class QuantumType(enum.Enum):
    Identity = enum.auto()
    Hadamard = enum.auto()
    X = enum.auto()
    RX = enum.auto()
    RXX = enum.auto()
    Y = enum.auto()
    RY = enum.auto()
    RYY = enum.auto()
    Z = enum.auto()
    RZ = enum.auto()
    RZZ = enum.auto()
    CX = enum.auto()
    CRX = enum.auto()
    CZ = enum.auto()

    def is_single_qubit(self):
        return self in {
            QuantumType.Identity,
            QuantumType.Hadamard,
            QuantumType.X,
            QuantumType.RX,
            QuantumType.Y,
            QuantumType.RY,
            QuantumType.Z,
            QuantumType.RZ,
        }

    def is_parameterized(self):
        return self in {
            QuantumType.RX,
            QuantumType.RXX,
            QuantumType.RY,
            QuantumType.RYY,
            QuantumType.RZ,
            QuantumType.RZZ,
            QuantumType.CRX,
        }


@dataclass(frozen=True)
class QuantumGate:
    type: QuantumType
    qubits: tuple[int] | tuple[int, int]


class ParametrizedQuantumCircuit:
    """
    A Quantum circuit representation to use in the Quantum Architecture Searches.
    It has methods for various proxies and stores the results as well, to have everything close.
    Allows easy access to the gates inside so it can be used by functions that use it.
    """

    qubits: int
    """How many qubits does the circuit contain"""

    gates: list[list[QuantumGate]]
    """Gates in the quantum circuit, organised as a list of layers of gates."""

    parameters: int
    """How many parameters are used the circuit"""

    _expressivity: float | None = None
    """
    Expressivity of the circuit, following the definition from {THE PAPER}
    Use `expressivity` to get the value
    """  # TODO: link paper

    _entanglement: float | None = None
    """
    Entanglement of the circuit, following the definition from {THE PAPER}
    Use `entanglement` to get the value
    """  # TODO: link paper

    _fidelity: float | None = None
    """
    Approximated fidelity of the circuit
    Use `fidelity` to get the value
    """

    _qiskit_circ: tuple[QuantumCircuit, ParameterVector] | None = None

    def __init__(self, qubits: int):
        """
        Initialise an empty circuit for the passed amount of qubits
        """
        self.qubits = qubits
        self.gates = []

    def append_layer(self, layer: list[QuantumGate]):
        """
        Add a layer to the end of the existing circuit in-place
        """
        for gate in layer:
            if gate.type.is_parameterized():
                self.parameters += 1
        self.gates.append(layer)

    @property
    def circ(self) -> tuple[QuantumCircuit, ParameterVector]:
        """
        Qiskit circuit version to be used for simulations etc.
        """
        if self._qiskit_circ is None:
            self._qiskit_circ = build_qiskit_circ(self)

        return self._qiskit_circ

    def expressivity(self, config: ProxyConfig) -> float:
        """
        Expressivity of the circuit, following the definition from {THE PAPER}
        """  # TODO: Link Paper
        if self._expressivity is None:
            self._expressivity = float(calculate_expressivity(self, config)[0])
        return self._expressivity

    def entanglement(self, config: ProxyConfig) -> float:
        """
        Entanglement of the circuit, following the definition from {THE PAPER}
        """  # TODO: Link Paper
        if self._entanglement is None:
            self._entanglement = float(calculate_entanglement(self, config)[0])

        return self._entanglement

    def fidelity(self, config: ProxyConfig) -> float:
        """
        Approximated fidelity of the circuit
        """
        if self._fidelity is None:
            self._fidelity = float(calculate_fidelity(self, config)[0])

        return self._fidelity
