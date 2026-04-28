
#import "@preview/touying:0.6.1": *
#import "@preview/physica:0.9.5": *
#import "@preview/cetz:0.5.0"
#import "@preview/typsium:0.2.0": ce
#import "@preview/numbly:0.1.0": numbly
#import "@preview/quill:0.7.2": *
#import "@preview/quill:0.7.2": tequila as tq
#import "./theme.typ": *

#set heading(numbering: numbly("{1}.", default: "1.1"))
#show ref: set text(size:0.5em, baseline: -0.75em)

#let cetz-canvas = touying-reducer.with(reduce: cetz.canvas, cover: cetz.draw.hide.with(bounds: true))


#show: university-theme.with(
  config-info(
    title: "Training-Free QAS", // Required
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


#title-slide()

#outline(depth: 1, title: text(fill: rgb("#00a6d6"))[Content])

= Introduction

== Variational Quantum Algorithms

- NISQ era

- Classical optimisation

- Parametrized Quantum Circuit

#pause
- Performance is circuit dependent

== Quantum Architecture Search

- Automated Parametrized Quantum Ciruit finding
  - Solution to circuit dependency

#pause
- New Problems
  - Exponential search space
  - Ranking circuits during search

#pause
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
  #text(fill: red)[- not done in paper@training-free]

= Method

== Overview

#align(horizon)[
The Steps of the protocol:
#pause
1. Sample circuits from search space

#pause
2. Filter using Path proxy

#pause
3. Rank on Expressibility
]

== Search Space

Following Neural Predictor based QAS@npqas
- Native gate set ($cal(A) = {R_x, R_y, R_z, X X, Y Y, Z Z}$)
#grid(
  columns: (auto, auto),
  rows: (auto, auto),
  gutter: 1em,
  [- Layer based sampling
    - Layers of $n/2$ gates
  ], grid.cell(rowspan:2)[
    #quantum-circuit(equal-row-heights: true, row-spacing: 0.8em, wires: 6, 1, $R_l$, 1,[\ ],[\ ],1,$R_l$, 1,[\ ],[\ ],1,$R_l$)
    #quantum-circuit(equal-row-heights: true, row-spacing: 0.8em, wires: 6, 3, [\ ], 1, $R_l$, 1,[\ ],[\ ],1,$R_l$, 1,[\ ],[\ ],1,$R_l$)
    #quantum-circuit(equal-row-heights: true, row-spacing: 1.35em, wires: 6, 1, ctrl(1), 1, [\ ], 1, targ(), 1,[\ ], 1, ctrl(1),[\ ],1,targ(), 1,[\ ], 1, ctrl(1),[\ ],1,targ())
  ],
  [- Gate based sampling
    - placing 1 gate at a time
  ], []
)
- Why not fully random circuits?
  - Mitigating barren plateaus
  - Mitigating high circuit depth
  #text(fill:purple)[- What is the difference with gate-based?]

== Path Proxy

#slide(composer: (auto, auto))[
- *'zero-cost'*
  - below $7.8 times 10^(-4)$s
  #text(fill:orange)[- $O("Operations" times "Qubits"^2)$]

#pause
1. Represent as Directed acyclic graph
#pause
2. Count distinct paths from input-to-output
#pause
3. Top-R highest path count circuits
][
  #meanwhile
  #image("tf-qas/circuit.png", height: 40%)
  #pause
  #image("tf-qas/dag.png")
  #text(size: 0.6em)[#align(right)[from Training-Free QAS@training-free]]
]

== Expressibility Proxy

Assumption: Expressibility $|->$ Performance
#pause
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

#pause
- Compared to
  - Network-Predictive QAS@npqas
  - Hardware-efficient ansatz@hea-kandala // but like, which one
  - Their random sampling

#pause
- Implementation details
  - TensorCircuit python package@tensorcircuit
  #pause
  #text(fill: red)[- No code so one cannot reproduce]

== Proxy combinations

#slide(composer: (auto, auto))[
  - Only Path
    - Fast proxy (each $~ 2 times 10^(-4) "s"$)
    - Many ADAM queries

  - Only Expressibility
    - Slower proxy (each $~ 0.21 "s"$)
    - Fewer queries (each $~ 10 "s"$)

  - Combined
    - Fast proxy filtering
    - Even fewer queries
][
  #image("tf-qas/table.png")
  #text(size: 0.6em)[#align(right)[from Training-Free QAS@training-free]]
]

== Comparison with State of the Art

#slide(composer: (1fr, auto))[
- Where do these come from?

- A lot fewer queries

- Shorter search times

#pause
However:
- No way to reproduce and check
][
  #image("tf-qas/outcomes.png", height: 85%)
  #text(size: 0.6em)[#align(right)[from Training-Free QAS@training-free]]
]

= Conclusion

== Takeaways

- Combining proxies

- Training-Free methods can work better than HEA

== What will I do (differently)

Sampling:
- Evolutionary Algorithm instead of random sampling
  - With hardware constraints
  - Can build on parts of "Genetic optimization of ansatz
    expressibility for enhanced variational quantum algorithm
    performance."@genetic-expressibility

#pause
Filtering:
- Noise proxy
- Better entanglement proxy

#pause
And of course: Share my code

#slide[
  == References <touying:unoutlined>
  #bibliography("references.bib", title: [])
]

