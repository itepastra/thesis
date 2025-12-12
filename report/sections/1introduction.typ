#import "@preview/classy-tudelft-thesis:0.1.0": *
#import "@preview/physica:0.9.6": *
#import "@preview/unify:0.7.1": num, numrange, qty, qtyrange
#import "@preview/zero:0.5.0"

= Introduction

In the NISQ era quantum-classical hybrid methods are better due to the limited depth, bla bla bla

There has been significant research into various methods of Quantum Architecture Search (QAS), 
(list a bunch).
Most of these have been searches that are specific to the problem that is being solved,
so the Paremetrized quantum circuits (PQCs) are generally not transferrable between different problems.

There has also been a bit of research into task-agnostic QAS, where search
can be performed once per hardware iteration instead of per problem, using proxies like expressibility
and entanglement (CITE THE PAPER). 
Where maybe some finetuning can help specialise into a specific problem afterwards. (HYPOTHETICAL)

These task-agnostic searches have yet to include things like noise, arbitrary connectivity graphs
and allowed gate types on a per-qubit basis. And also haven't shown great scalability to architectures
with more qubits.

This research proposes a Task-Agnostic Evolutionary QAS implementing 
hardware constraints and noise profiles able to target circuits with a 
user-specified expressibility and entanglement to be able to mitigate the barren plateaus from
an expressibility that's too high (cite).

To achieve these goals a python library will be made that allows for composing various filters
and generators together (with multithreading) to help with developing and iterating on QAS methods.

