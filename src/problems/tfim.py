import numpy as np

dt = np.dtype(np.float64)


def _pauli_x() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=dt)


def _pauli_z() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=dt)


def _ident() -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    return np.eye(2, dtype=dt)


def kronecker_product(
    gates: list[np.ndarray[tuple[int, int], np.dtype[np.float64]]],
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    out: np.ndarray[tuple[int, int], np.dtype[np.float64]] = np.array([[1.0]], dtype=dt)
    for op in gates:
        out = np.kron(out, op)
    return out


# TODO: make a test to ensure this is correct
def tfim_hamiltonian(
    n: int, periodic: bool = True
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    X = _pauli_x()
    Z = _pauli_z()
    I = _ident()
    dimension = 1 << n
    H = np.zeros((dimension, dimension), dtype=dt)

    for i in range(n):
        operations = [I] * n
        operations[i] = X
        H += kronecker_product(operations)

        j = (i + 1) % n
        if (not periodic) and (j == 0):
            continue
        operations[i] = Z
        operations[j] = Z
        H += kronecker_product(operations)

    return H


# TODO: make a test to ensure this is correct
def exact_ground_energy(H: np.ndarray[tuple[int, int], np.dtype[np.float64]]) -> float:
    w = np.linalg.eigvalsh(H)
    return float(w[0])
