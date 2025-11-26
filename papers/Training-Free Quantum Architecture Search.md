AAAI <- blijkbaar goeie

= The process

1. sample N random circuits
2. Calculate the number of paths through the DAG.
3. sort by number of paths
4. filter top-R
5. Calculate expressibility for each C in top-R
6. output top-K circuits


= The search-space

This search space is used to generate the random circuits to sample from, in the paper they use two(?) methods

== Layerwise

In this seach space they apply a certain gate type to either all even or all odd qubits.

== Gatewise with IBM's topology

Here they only allow gates available on the topology



= Glossary

What the heck do the terms they're using all mean.

== Query

I presume something like "try to optimize this circuit on the quantum computer"
but **I'm unsure**

== PQAS

Either Neural Predictor based QAS or, GradSign or Tensorcircuit

Probably the Neural Predictor one. (more [here]())

== QAS

Quantum Architecture Search

== HEA-3 till 5

Hardware Efficient Ansatze, specifically number 3 to 5 from ([this paper](https://www.nature.com/articles/nature23879))
