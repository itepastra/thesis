#import "@preview/classy-tudelft-thesis:0.1.0": *
#import "@preview/physica:0.9.6": *
#import "@preview/unify:0.7.1": num, numrange, qty, qtyrange
#import "@preview/zero:0.5.0"

= Introduction

Quantum computers capable of performing the widely recognised algorithms 
like Shor's factorisation algorithm // TODO: cite
and large data Grovers Search // TODO: cite
are not techonologically feasible yet. // TODO: add citations

This is due to the current quantum computers still having noisy qubits that which limits
the circuit depth of algorithms that can be performed. They also have a limited amout of qubits,
which is why this era of quantum computing is called the Noisy Intermediate-Scale Quantum (NISQ) era.

This does not mean there are no uses for these NISQ quantum computers,
Quantum Machine Learning and other quantum-classical methods are still promising prospects.
Diverse real-world practical capabilities have been demonstrated like // TODO: list with citations

The quantum-classical methods start with a quantum circuit that contains some amount of parametrized
gates, called Parametrized Quantum Circuits or PQCs for short. This PQC is used with a training set
where a classical computer takes measurement results and optimises the parameters to solve a problem.

// TODO: find some way to explain why QAS is necessary here

To address these challenges methods have been proposed for automatically finding the PQC,
also known as Quantum Architecture Search (QAS), 
which can solve the problem like: ... // TODO: list with citations

Most of these solutions evaluate performance of the circuit with optimisation during the search,
these classical optimisations take a significant amount of time and are therefore not very scalable.
// TODO: add citations
Some of the solutions /* TODO: add citations to TF-QAS and evolutionary expressibility */ use
proxies to optimize a PQC without any quantum-classical optimization, however they do not implement
hardware constraints and noise patterns which may limit their applicability on real hardware.

To address these limitations we propose QD-QAS, // Quality-Diversity Quantum Architecture Search
a problem-agnostic yet hardware-specific quantum architecture search based on hardware topology,
noise patters and gatesets.

// These are just goals atm, but can be made concrete once I did them
- We use Quality-Diversity Evolutionary Algorithms trained using proxies for Expressibility,
  Entanglement, and Noise to create a diverse set of PQCs to make sure every problem has a
  PQC that works well.
- We benchmark this algorithm on both runtime and performance in against, TF-QAS@training-free,
  Random Sampling and GA-QAS@genetic-expressibility. Since both TF-QAS and GA-QAS don't include
  noise but QD-QAS does we will compare under multiple types and amounts of noise.
- We also develop an open-source python library to efficiently work with Evolutionary algorithms 
  combined with various proxies that is easily extendable to new usecases.
