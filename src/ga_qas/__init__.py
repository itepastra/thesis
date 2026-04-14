from collections.abc import Callable
from dataclasses import dataclass
from operator import itemgetter
from random import Random

from tqdm import tqdm

from quantum_circuit import ParametrizedQuantumCircuit, QuantumGate, QuantumType


@dataclass
class GeneticAlgorithmSettings:
    qubits: int

    depth: int

    cost_function: Callable[[list[ParametrizedQuantumCircuit]], list[float]]
    """A function that takes a list of PQC's and returnes the cost of each"""

    sample_function: Callable[[Random], ParametrizedQuantumCircuit]
    """A function that returns a random PQC"""
    initial_population_size: int

    offspring_size: int

    survival_size: int

    mutation_rate: float

    generations: int

    gate_set: list[QuantumType]


def crossover_once(
    p1: ParametrizedQuantumCircuit, p2: ParametrizedQuantumCircuit, random: Random
) -> list[list[QuantumGate]]:
    crossover_layer = random.randrange(1, len(p2.gates))
    return p1.gates[:crossover_layer] + p2.gates[crossover_layer:]


def crossover_many(
    p1: ParametrizedQuantumCircuit, p2: ParametrizedQuantumCircuit, random: Random, crossover_odds: float
) -> list[list[QuantumGate]]:
    crossover_map = [random.random() < crossover_odds for layer in p1.gates]
    final = []
    active = p1
    for i in range(len(p1.gates)):
        if crossover_map[i]:
            active = p2 if active == p1 else p1
        final.append(active.gates[i])
    return final


def ga_qas(
    settings: GeneticAlgorithmSettings, random: Random
) -> tuple[list[tuple[float, float]], list[tuple[ParametrizedQuantumCircuit, float]]]:
    initial_population: list[ParametrizedQuantumCircuit] = [
        settings.sample_function(random) for i in range(settings.initial_population_size)
    ]

    return_data: list[tuple[float, float]] = []

    population: list[ParametrizedQuantumCircuit] = initial_population
    best_circuits: list[ParametrizedQuantumCircuit] = []

    for generation in tqdm(range(settings.generations), desc="Generations", position=0):
        pop_cost = settings.cost_function(population)
        parents: list[ParametrizedQuantumCircuit] = [
            x for x, _ in sorted(zip(population, pop_cost), key=itemgetter(1))
        ][: settings.survival_size]
        offspring: list[ParametrizedQuantumCircuit] = []
        best_circuits.append(parents[0])

        for _ in tqdm(range(settings.offspring_size), desc="Generating offspring", position=1, leave=False):
            [p1, p2] = random.sample(parents, 2)
            assert isinstance(p1, ParametrizedQuantumCircuit), f"expected PQC, but found {p1}"
            assert isinstance(p2, ParametrizedQuantumCircuit), f"expected PQC, but found {p2}"
            child_layers = crossover_once(p1, p2, random)
            if random.random() < settings.mutation_rate:
                layer_idx = random.randrange(settings.depth)
                layer = child_layers[layer_idx]
                gate_idx = random.randrange(len(layer))
                old_gate = child_layers[layer_idx][gate_idx]

                if old_gate.type.is_single_qubit():
                    child_layers[layer_idx][gate_idx] = QuantumGate(
                        random.choice([gate for gate in settings.gate_set if gate.is_single_qubit()]), old_gate.qubits
                    )
                else:
                    child_layers[layer_idx][gate_idx] = QuantumGate(
                        old_gate.type, (old_gate.qubits[1], old_gate.qubits[0])
                    )
            assert len(child_layers) == settings.depth, f"{child_layers} does not have depth {settings.depth}"
            for i, layer in enumerate(child_layers):
                assert layer, f"layer {i} is empty"
            child = ParametrizedQuantumCircuit(settings.qubits)
            child.extend_layers(child_layers)
            offspring.append(child)
        population = offspring
        old_pop_cost = pop_cost
        pop_cost = settings.cost_function(population)

        return_data.append((min(old_pop_cost), min(pop_cost)))
    return (return_data, sorted(zip(population, pop_cost), key=itemgetter(1)))
