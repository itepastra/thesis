== Introduction
What I'll be making is a program that uses a Hardware discriptor 
-like the one exported by qiskit- together with a target expressibility, 
target entanglement, and a minimal Fidelity to produce a 
diverse set of Parametrised Quantum Circuits (PQCs). 
Unlike previous training free Quantum Architecture Searches@training-free@evolutionary-architecture-search
we will make the search hardware-specific while also keeping it training-free 
and target a specific expressibility instead of just maximizing to help mitigate barren plateaus.
The program will be using one of the Quality-Diversity Evolutionary Algorithms@qdea to achieve this,
the quality aspect will use the Expressibility, Entanglement, and simulated Noise -or proxies for these-
to determine the Quality, while some measure of distance between different expressible Hilbert Spaces
will be developed to help the algorithm with the Diversity aspect.
We opt for a modular but integrated approach where it's simple to modify, add, or remove proxies
from the Evolutionary Algorithm, this way the system can be built upon for future research.
In the next parts I'll list the inputs and outputs in a more structured way.

= Inputs
- Hardware description (like in Qiskit for example)
  - Topology: Connection graph between qubits
  - Valid gates: Valid hardware gates on each qubit/connection
  - Fidelities of gates: Gate fidelity on a per-qubit/connection basis
  - Decoherence times: Decoherence times of each qubit
- Target Expressibility: Expressibility that should be searched towards, both lower and higher than the target will be penalised by the cost function
- Target Entanglement: Entanglement that should be searched towards, also penalises both ways
- Minimal Fidelity: Circuits with a lower output fidelity than this will get penalised

= Outputs

- The set of optimised PQCs that cover a diverse set of areas on the Hilbert space
  - each circuit will balance diversity and performance (based on input targets)
  - each circuit will have a one-to-one trivial mapping to the hardware due to hardware descriptor input
- The final values of each used proxy per circuit
  - Expressibility
  - Entanglement
  - Fidelity


== References

#bibliography("references.bib")
