
#import "@preview/touying:0.6.1": *
#import "@preview/physica:0.9.5": *
#import "@preview/cetz:0.3.4"
#import "@preview/typsium:0.2.0": ce
#import "@preview/numbly:0.1.0": numbly
#import "./theme.typ": *

#set heading(numbering: numbly("{1}.", default: "1.1"))
#show ref: set text(size:0.5em, baseline: -0.75em)

#let cetz-canvas = touying-reducer.with(reduce: cetz.canvas, cover: cetz.draw.hide.with(bounds: true))


#show: university-theme.with(
  config-info(
    title: "Implementation Specific QAS", // Required
    date: datetime.today().display(),
    authors: ("Noa Aarts"),
  
    // Optional Styling (for more / explanation see in the typst universe)
    // ignore how bad the images look i'll adjust it until Monday
    title-color: blue.darken(10%),
  ),
  config-common(
    // handout: true, // enable this for a version without animations
  ),
  aspect-ratio: "16-9",
  config-colors(
   primary: rgb("#00a6d6"),
   secondary: rgb("#00b3dc"),
   tertiary: rgb("#b8cbde"),
   neutral-lightest: rgb("#ffffff"),
   neutral-darkest: rgb("#000000"),
 ),
)

#show outline.entry: it => link(
  it.element.location(),
   text(fill: rgb("#00b3dc"), size: 1.3em)[#it.indented(it.prefix(), it.body())],
)


#slide[
- #text(fill: purple)[Purple text is a question I have]
- #text(fill: red)[Red text is something I think they did not do well]
- #text(fill: orange)[Orange text is something I would have preferred a reference for]
]

#title-slide()

#outline(depth: 1, title: text(fill: rgb("#00a6d6"))[Content])

= Introduction

== Variational Quantum Algorithms
 
- Classical optimisation

- Parametrized Quantum Circuit

- Very structure dependent

== Quantum Architecture Search

- Automated Design

- New Problems
  - Exponential search space
  - Ranking circuits during search

- Parallels with Neural Architecture Search
  - Differentiable QAS
  - Reinforcement-learning QAS
  - Predictor-based QAS
  - Weight-sharing QAS

== Training Free Proxies

- No need to train parametrized quantum circuit
  \ $->$ Faster searching

- No objective functions
  - Possibility for easier transfer

- Need to prove correlation with ground-truth
  #text(fill: red)[- not done in paper]

= Method

== Overview

#align(horizon)[
1. Sample circuits from search space

2. Filter using Path proxy

3. Rank on Expressibility
]

== Search Space

Following Neural Predictor based QAS@npqas
- Native gate set ($cal(A) = {R_x, R_y, R_z, X X, Y Y, Z Z}$)
- Layer based sampling
  - Layers of $n/2$ gates
- Gate based sampling
  - placing 1 gate at a time

- Why not fully random circuits?
  - Mitigating barren plateaus
  - Mitigating high circuit depth
  #text(fill:purple)[- What is the difference with gate-based?]

== Path Proxy

#slide(composer: (auto, auto))[
- 'zero-cost'
  #text(fill:orange)[- best case: $O("Operations" times "Qubits"^2)$] 
  // I think it'd scale like this, but am uncertain since they didn't explain it anywhere
  - below $7.8 times 10^(-4)$s

1. Represent as Directed acyclic graph

2. Count distinct paths from input-to-output

3. Top-R highest path count circuits
][
  #image("tf-qas/circuit.png", height: 40%)
  #image("tf-qas/dag.png")
  #text(size: 0.6em)[#align(right)[from Training-Free QAS@training-free]]
]

== Expressibility Proxy

#text(fill: red)[- Performance hinges on Expressibility]
- Particularly valueable without prior knowledge

#block(fill: blue.lighten(85%), inset: 12pt, radius: 6pt, stroke: 2pt + blue)[
  *Expressibility:* \ 
  The capability to uniformly reach the entire Hilbert space.
]

1. Calculate expressibility:
#align(center)[$cal(E)(cal(C)) = -D_"KL" (P(cal(C),F) || P_"Haar" (F)$]

2. Top expressibility circuits

= Results

== Evaluation

- Three variational quantum eigensolver tasks
  - Transverse field Ising model
  - Heisenberg model
  - $"Be"space.hair"H"_2$ molecule

- Compared to
  - Network-Predictive QAS@npqas
  #text(fill: red)[- Hardware-efficient ansatz@hea-kandala] // but like, which one
  - Random sampling

- Implementation details
  - TensorCircuit python package@tensorcircuit
  #text(fill: red)[- No code included anywhere]


= Conclusion

==

- Combining proxies can improve on either



#slide[
  == References <touying:unoutlined>
  #bibliography("references.bib", title: [])
]

