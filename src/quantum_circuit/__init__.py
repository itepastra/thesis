import enum
import re
from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit.circuit.parametervector import ParameterVector

from quantum_circuit.proxies.entanglement import calculate_entanglement
from quantum_circuit.proxies.expressivity import calculate_expressivity, calculate_fidelity
from quantum_circuit.proxy_config import ProxyConfig
from quantum_circuit.qiskit_helpers import build_qiskit_circ


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


ALL_GATE_TYPES = [
    QuantumType.Identity,
    QuantumType.Hadamard,
    QuantumType.X,
    QuantumType.RX,
    QuantumType.RXX,
    QuantumType.Y,
    QuantumType.RY,
    QuantumType.RYY,
    QuantumType.Z,
    QuantumType.RZ,
    QuantumType.RZZ,
    QuantumType.CX,
    QuantumType.CRX,
    QuantumType.CZ,
]


@dataclass(frozen=True)
class QuantumGate:
    type: QuantumType
    qubits: tuple[int] | tuple[int, int]

    def bitset(self) -> int:
        return sum(1 << pos for pos in self.qubits)


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

    layer_bitsets: list[int]
    """Bitset of used qubits for each layer"""

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

    def __str__(self):
        return str(self.circ[0])

    def __init__(self, qubits: int):
        """
        Initialise an empty circuit for the passed amount of qubits
        """
        self.qubits = qubits
        self.gates: list[list[QuantumGate]] = []
        self.layer_bitsets: list[int] = []
        self.parameters = 0

    def append_layer(self, layer: list[QuantumGate], collapse: bool):
        """
        Add a layer to the end of the existing circuit in-place
        """
        if collapse and self.gates:
            add_to_prev = True
            prev_positions = self.layer_bitsets[-1]
            for gate in layer:
                gate_bitset = gate.bitset()
                if gate_bitset & prev_positions:
                    add_to_prev = False
                    self.layer_bitsets.append(0)
                    break
        else:
            add_to_prev = False
            self.layer_bitsets.append(0)

        for gate in layer:
            self.layer_bitsets[-1] |= gate.bitset()

        if add_to_prev:
            self.gates[-1].extend(layer)
        else:
            self.gates.append(layer)
        assert len(self.gates) == len(
            self.layer_bitsets
        ), f"Desync between {self.gates} and {self.layer_bitsets}"

    def extend_layers(self, layers: list[list[QuantumGate]]):
        """
        Add multiple layers to the existing circuit in-place
        """
        for layer in layers:
            self.append_layer(layer, False)

    def append_gate(self, gate: QuantumGate):
        """
        Add a gate in the first spot that is valid
        """

        gate_qubits = gate.bitset()
        earliest_empty: int | None = None

        depth = len(self.gates)
        for rev_idx, (layer, bits) in enumerate(
            zip(reversed(self.gates), reversed(self.layer_bitsets)), 1
        ):
            idx = depth - rev_idx
            if gate_qubits & bits:
                break
            else:
                earliest_empty = idx

        if earliest_empty is None:
            self.gates.append([gate])
            self.layer_bitsets.append(gate.bitset())
        else:
            self.gates[earliest_empty].append(gate)
            self.layer_bitsets[earliest_empty] |= gate.bitset()
        assert len(self.gates) == len(
            self.layer_bitsets
        ), f"Desync between {self.gates} and {self.layer_bitsets}"

    def check_parameters(self, notify=True):
        parameters_found = 0

        for layer in self.gates:
            for gate in layer:
                if gate.type.is_parameterized():
                    parameters_found += 1

        if parameters_found != self.parameters:
            if notify:
                print(
                    f"wrong amount of parameters found, was {self.parameters}, now {parameters_found}"
                )
            self.parameters = parameters_found

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
