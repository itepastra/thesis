import pytest

from quantum_circuit import QuantumType


@pytest.mark.parametrize(
    "type,expected",
    [
        (QuantumType.Identity, True),
        (QuantumType.Hadamard, True),
        (QuantumType.CZ, False),
        (QuantumType.CRX, False),
        (QuantumType.CX, False),
        (QuantumType.RX, True),
        (QuantumType.RXX, False),
        (QuantumType.RY, True),
        (QuantumType.RYY, False),
        (QuantumType.RZ, True),
        (QuantumType.RZZ, False),
        (QuantumType.X, True),
        (QuantumType.Y, True),
        (QuantumType.Z, True),
    ],
)
def test_is_single_qubit_correct(type: QuantumType, expected: bool):
    assert type.is_single_qubit() == expected


@pytest.mark.parametrize(
    "type,expected",
    [
        (QuantumType.Identity, False),
        (QuantumType.Hadamard, False),
        (QuantumType.CZ, False),
        (QuantumType.CRX, True),
        (QuantumType.CX, False),
        (QuantumType.RX, True),
        (QuantumType.RXX, True),
        (QuantumType.RY, True),
        (QuantumType.RYY, True),
        (QuantumType.RZ, True),
        (QuantumType.RZZ, True),
        (QuantumType.X, False),
        (QuantumType.Y, False),
        (QuantumType.Z, False),
    ],
)
def test_is_parametrized_correct(type: QuantumType, expected: bool):
    assert type.is_parameterized() == expected
