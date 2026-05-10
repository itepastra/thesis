import pytest

from quantum_circuit import GateType


@pytest.mark.parametrize(
    "type,expected",
    [
        (GateType.Identity, True),
        (GateType.Hadamard, True),
        (GateType.CZ, False),
        (GateType.CRX, False),
        (GateType.CX, False),
        (GateType.RX, True),
        (GateType.RXX, False),
        (GateType.RY, True),
        (GateType.RYY, False),
        (GateType.RZ, True),
        (GateType.RZZ, False),
        (GateType.X, True),
        (GateType.Y, True),
        (GateType.Z, True),
    ],
)
def test_is_single_qubit_correct(type: GateType, expected: bool):
    assert type.is_single_qubit() == expected


@pytest.mark.parametrize(
    "type,expected",
    [
        (GateType.Identity, False),
        (GateType.Hadamard, False),
        (GateType.CZ, False),
        (GateType.CRX, True),
        (GateType.CX, False),
        (GateType.RX, True),
        (GateType.RXX, True),
        (GateType.RY, True),
        (GateType.RYY, True),
        (GateType.RZ, True),
        (GateType.RZZ, True),
        (GateType.X, False),
        (GateType.Y, False),
        (GateType.Z, False),
    ],
)
def test_is_parametrized_correct(type: GateType, expected: bool):
    assert type.is_parameterized() == expected
