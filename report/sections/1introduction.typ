#import "@preview/classy-tudelft-thesis:0.1.0": *
#import "@preview/physica:0.9.6": *
#import "@preview/unify:0.7.1": num, numrange, qty, qtyrange
#import "@preview/zero:0.5.0"

= Introduction

== Before starting
Okay, so as far as I currently know a Variational Quantum Eigensolver (VQE) is a semi-quantum way to find eigenvalues
for a matrix.
They currently are mostly using Hardware Efficient Ansatze. // TODO: needs facts
These Ansatze are optimized for relatively small connectivity, and don't keep errors into account that much.
I want to figure out if this can be done better, by using a descriptor format of the hardware including connections
between qubits etc. is it possible to make ansatze that are better in
- fewer parameters
- less error prone
- speed of optimisation

That is what I will go and try figuring out I think
