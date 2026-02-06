#!/usr/bin/env python
# This is a replication attempt of
# "Genetic optimization of ansatz expressibility for enhanced variational quantum algorithm performance"

import random
import sys

from qas_flow import Stream
from quantum_circuit import (Gate, GateType, QuantumCircuit, circ_from_layers,
                             sample_random_generator, single_typ)
from sampling_hyperparams import sample_hyperspace

gate_set: list[GateType] = [GateType.H, GateType.RX, GateType.RY, GateType.RZ, GateType.CRX, GateType.CX]


EXPRESSIBILITY_SAMPLES: int = 2000


def run_ga_qas(
    depth: int, qubits: int, generations: int, generation_size: int, parent_amount: int, mutation_rate: float, seed: int
) -> list[tuple[int, int, int, int, int, float, float, float]]:

    print(
        f"running GA QAS {seed} with {qubits} qubits, {depth} depth, for {generations} generations of size {generation_size}, with {parent_amount} parents and {mutation_rate:.3f} mutation rate",
        file=sys.stderr,
    )

    seed_rng = random.Random(seed)
    initial_population: list[QuantumCircuit] = (
        Stream(sample_random_generator(random.Random(seed_rng.randint(1000, 1000000000)), qubits, depth, gate_set))
        .apply(lambda circ: circ.expressibility_estimate(EXPRESSIBILITY_SAMPLES, seed_rng.randint(1000, 1000000000)))
        .take(generation_size)
        .collect()
    )

    population: list[QuantumCircuit] = initial_population
    main_rng = random.Random(seed_rng.randint(1000, 1000000000))

    best_circuits: list[QuantumCircuit] = []
    return_data: list[tuple[int, int, int, int, int, float, float, float]] = []
    for generation in range(generations):
        print(f"starting generation {generation} for seed {seed}", file=sys.stderr)
        population.sort(key=lambda qc: qc.expressibility, reverse=True)
        parents: list[QuantumCircuit] = population[:parent_amount]
        offspring: list[QuantumCircuit] = []
        for _ in range(generation_size):
            [p1, p2] = main_rng.sample(parents, 2)
            crossover_layer = main_rng.randint(1, depth)
            child_layers = p1.gates[:crossover_layer] + p2.gates[crossover_layer:]
            if main_rng.random() < mutation_rate:
                layer_idx = main_rng.randrange(depth)
                layer = child_layers[layer_idx]
                gate_idx = main_rng.randrange(len(layer))
                old_gate = child_layers[layer_idx][gate_idx]

                if old_gate.single():
                    child_layers[layer_idx][gate_idx] = Gate(
                        main_rng.choice([gate for gate in gate_set if single_typ(gate)]),
                        old_gate.qubits,
                        old_gate.param_idx,
                    )
                else:
                    child_layers[layer_idx][gate_idx] = Gate(
                        old_gate.typ, (old_gate.qubits[1], old_gate.qubits[0]), old_gate.param_idx
                    )

            child = circ_from_layers(child_layers, qubits)
            child.expressibility_estimate(2000, seed_rng.randint(1000, 1000000000))
            offspring.append(child)

        offspring.sort(key=lambda qc: qc.expressibility, reverse=True)
        return_data.append(
            (
                depth,
                qubits,
                generation,
                generation_size,
                parent_amount,
                mutation_rate,
                population[0].expressibility,
                offspring[0].expressibility,
            )
        )
        if population[0].expressibility > offspring[0].expressibility:
            best_circuits.append(population[0])
        else:
            best_circuits.append(offspring[0])
        population = offspring
    print(f"finished seed {seed}, data: {return_data}", file=sys.stderr)
    return return_data


def run_from_point(pnt: tuple[tuple[int, int, int, int, float], int]):
    (point, seed) = pnt
    try:
        return run_ga_qas(point[0], point[1], 20, point[2], point[3], point[4], seed)
    except:
        print(f"There was an error for {point}, {seed}, ignoring it")
        return []


def print_ret(ret_data):
    for dat in ret_data:
        (depth, qubits, generation, generation_size, parent_amount, mutation_rate, best_pop, best_offspring) = dat
        print(
            f"{depth},{qubits},{generation},{generation_size},{parent_amount},{mutation_rate},{best_pop},{best_offspring}",
            flush=True,
        )


def main() -> None:

    rng = random.Random()

    results: list[QuantumCircuit] = (
        Stream(sample_hyperspace((1, 40), (1, 10), (1, 100), (1, 20), (0.0, 1.0), seed=rng.randint(1000, 1000000000)))
        .map(lambda point: (point, rng.randint(1000, 1000000000)))
        .par_map(run_from_point)
        .apply(print_ret)
        .collect()
    )


if __name__ == "__main__":
    main()
