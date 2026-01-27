#!/usr/bin/env python
# This is a replication attempt of
# "Genetic optimization of ansatz expressibility for enhanced variational quantum algorithm performance"

import random

import matplotlib.pyplot as plt

from qas_flow import Stream
from quantum_circuit import (Gate, GateType, QuantumCircuit, circ_from_layers,
                             sample_random_generator, single_typ)

DEPTH: int = 6
QUBITS: int = 6
GENERATIONS: int = 40
GENERATION_SIZE: int = 60
PARENT_AMOUNT: int = 10
MUTATION_RATE: float = 0.1


gate_set: list[GateType] = [
    GateType.H,
    GateType.RX,
    GateType.RY,
    GateType.RZ,
    GateType.CRX,
    GateType.CX,
]


def sample_hyperspace(*args: tuple[int, int] | tuple[float, float]):
    minimums: list[float | int] = [arg[0] for arg in args]
    maximums: list[float | int] = [arg[1] for arg in args]

    while True:
        yield ()


def plot_best_circuits(best_circuits: list[QuantumCircuit]) -> None:
    fig, ax = plt.subplots()

    ax.plot([-circ.expressibility for circ in best_circuits])
    fig.savefig("best_circuits.png")


def main() -> None:
    seed_rng: random.Random = random.Random(1020381)
    initial_population: list[QuantumCircuit] = (
        Stream(sample_random_generator(random.Random(101020), QUBITS, DEPTH, gate_set))
        .apply(lambda circ: print(circ))
        .apply(
            lambda circ: circ.expressibility_estimate(
                2000, seed_rng.randint(1000, 1000000000)
            )
        )
        .apply(lambda circ: print(circ))
        .take(GENERATION_SIZE)
        .collect()
    )

    population = initial_population

    main_rng = random.Random(2837175)

    best_circuits: list[QuantumCircuit] = []

    for generation in range(GENERATIONS):
        print(f"starting generation {generation}")
        population.sort(key=lambda qc: qc.expressibility, reverse=True)
        parents = population[:PARENT_AMOUNT]
        for parent in parents:
            print(parent)
        offspring = []
        for _ in range(GENERATION_SIZE):
            [p1, p2] = main_rng.sample(parents, 2)
            crossover_layer = main_rng.randint(1, DEPTH)
            child_layers = p1.gates[:crossover_layer] + p2.gates[crossover_layer:]
            if main_rng.random() < MUTATION_RATE:
                layer_idx = main_rng.randrange(DEPTH)
                layer = child_layers[layer_idx]
                gate_idx = main_rng.randrange(len(layer))
                old_gate = child_layers[layer_idx][gate_idx]

                if old_gate.single():
                    child_layers[layer_idx][gate_idx] = Gate(
                        main_rng.choice(
                            [gate for gate in gate_set if single_typ(gate)]
                        ),
                        old_gate.qubits,
                        old_gate.param_idx,
                    )
                else:
                    child_layers[layer_idx][gate_idx] = Gate(
                        old_gate.typ,
                        (old_gate.qubits[1], old_gate.qubits[0]),
                        old_gate.param_idx,
                    )

            child = circ_from_layers(child_layers, QUBITS)
            child.expressibility_estimate(2000, seed_rng.randint(1000, 1000000000))
            offspring.append(child)

        offspring.sort(key=lambda qc: qc.expressibility, reverse=True)
        if population[0].expressibility > offspring[0].expressibility:
            print(f"best parent > best child")
            best_circuits.append(population[0])
        else:
            print(f"best child > best parent")
            best_circuits.append(offspring[0])
        population = offspring

    plot_best_circuits(best_circuits)
    plt.show()


if __name__ == "__main__":
    main()
