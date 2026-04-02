from collections.abc import Callable

from quantum_circuit import ParametrizedQuantumCircuit


def benchmark_qas(
    qas_results: list[ParametrizedQuantumCircuit],
    problem_function: Callable[[ParametrizedQuantumCircuit], tuple[bool, ...]],
    continue_after_found: bool = False,
):
    for i, circ in enumerate(qas_results):
        result = problem_function(circ)
        if result[0]:
            print(f"Circ\n{circ}\nat index {i} succeeded")
            if not continue_after_found:
                break
