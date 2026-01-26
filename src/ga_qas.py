#!/usr/bin/env python
# This is a replication attempt of
# "Genetic optimization of ansatz expressibility for enhanced variational quantum algorithm performance"

import random
from quantum_circuit import (
    Gate,
    GateType,
    QuantumCircuit,
    circ_from_layers,
    sample_random_generator,
)
from qas_flow import Stream

DEPTH = 20
QUBITS = 5
GENERATIONS = 20
GENERATION_SIZE = 20
PARENT_AMOUNT = 5
MUTATION_RATE = 0.1


def main():
    seed_rng = random.Random(1020381)
    initial_population: list[QuantumCircuit] = (
        Stream(sample_random_generator(random.Random(101020), QUBITS, DEPTH))
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
                match old_gate.type:
                    case GateType.H | GateType.RX | GateType.RY | GateType.RZ:
                        child_layers[layer_idx][gate_idx] = Gate(
                            main_rng.choice(
                                [GateType.H, GateType.RX, GateType.RY, GateType.RZ]
                            ),
                            old_gate.qubits,
                            old_gate.param_idx,
                        )
                    case GateType.CRX | GateType.CX:
                        child_layers[layer_idx][gate_idx] = Gate(
                            old_gate.type,
                            tuple(old_gate.qubits[::-1]),
                            old_gate.param_idx,
                        )
                    case _:
                        print(f"unhandled gate: {old_gate}")
            child = circ_from_layers(child_layers, QUBITS)
            child.expressibility_estimate(2000, seed_rng.randint(1000, 1000000000))
            offspring.append(child)
        population = offspring


if __name__ == "__main__":
    main()
