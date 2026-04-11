#import "@preview/touying:0.6.1": *
#import "@preview/physica:0.9.5": *
#import "@preview/cetz:0.3.4"
#import "@preview/typsium:0.2.0": ce
#import "@preview/numbly:0.1.0": numbly
#import "@preview/fletcher:0.5.8": *
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

#let chev(start, len, f: none, offset: -0.4) = {
  import cetz.draw: *
  line(fill: f,
    cetz.vector.add(start,(offset, -1))
  , cetz.vector.add(start, (len + offset, -1))
  , cetz.vector.add(start,(len, 0))
  , cetz.vector.add(start, (len + offset, 1))
  , cetz.vector.add(start,(offset,1))
  , start
  , cetz.vector.add(start,(offset,-1)))
}

#let lg(color1, color2) = gradient.linear(color2, color1, color2, angle: 90deg)

#let today-offset = (datetime.today() - datetime(day: 10, month: 11, year: 2025)).weeks()

= Week ??

Post Surgery

== Content

- Research question
- Solution Architecture
- Comparing with other methods

== Research Question

- Uncertain about the wording
#pause
How does Quality-Diversity based Quantum Architecture Search compare to the state-of-the-art in QAS
in speed, noise performance and transferability between problems?

== Hypothesis

I think the speed of the search itself will be comparable to the GA-QAS, which is slower than
TF-QAS but likely faster then problem specific searches.

In noise performance I think it would be possible to improve upon both GA-QAS and TF-QAS as neither
attempts to optimize for it.

I think the transferability of the output will be a significant improvement over TF-QAS,
especially when counting the whole set of PQCs.

== QD-QAS architecture

#let nodes = ("Make Initial Population", "Create Offspring", "Calculate Cost Function", "Take Best Offspring", "Offspring Becomes Parents")
#let edges = (
  (0, 1),
  (1, 2),
  (2, 3),
  (3, 4),
  (4, 1),
)
#align(center + horizon)[
#diagram({
	for (i, n) in nodes.enumerate() {
		let θ = -90deg + i*360deg/nodes.len()
		node((θ, 0.8), n, stroke: 0.5pt, name: str(i))
	}
	for (from, to) in edges {
		let bend = if (to, from) in edges { 10deg } else { 5deg }
		// refer to nodes by label, e.g., <1>
		edge(label(str(from)), label(str(to)), "-|>", bend: bend)
	}
})
]

== Similarities/Differences with GA-QAS

- Same global structure
- Cost function for QD-QAS includes "distance"

== Calculating Distance

I have some ideas, but need to decide on which are most promising

structural:
- differences in gates
- differences in connection graph
#pause
behavioural:
- explored "area" of Hilbert space overlap
- shape of histogram compared with HAAR
- difference between 'average' vectors from sampling


== Comparing

- Preferences
  - Same benchmarks for all QAS types
  - Not implementing tests multiple times
  - Consistent program outputs


== Comparing

- Options I see
  - Replicate other papers to have consistent outputs \
    \- need to get it all working as expected \
    \+ will have identical tests and outputs
  - Create an interface and adapt the other papers to it \
    \- limited by the lowest common denominator \
    \+ don't need to fully replicate papers
  - Use the tests of the other papers \
    \- Likely can't compare all together \
    \- Can't choose tests freely \
    \+ Not necessary to rerun tests of the other papers \
    \+ Don't have to implement tests for the other papers

== Comparing

Prefer Replicating:
- As far as I know the searches themselves are already replicated
- Makes consistent testing possible

== Testing

- What are good comparisons?
  - TFIM
  - BeH
  - random unitaries
- compare transferability
  - run search once, then all tests on the same test


= Week 12
Making Baselines

== Holiday and personal life

- Holiday was very relaxed, didn't do a lot
- I have a boyfriend now
- I have surgery on feb-18
  - makes it hard to concentrate on university right now
- finished up QCQP course
- Starting grading of FQI exams, I might do it over the weekend

== Training-Free QAS@training-free

- Tried to reproduce, but circuits did not end up admissible.
  - still didn't work with sampling change
  - was not even close, at least a 10x worse performance of the outputs
  - probably missed a step
- Similar performance in time though
- Sent a mail to the correspondent author

== Genetic Algorithm QAS@genetic-expressibility

- Tried to reproduce
  - the circuits get mixed
  - I can sort on the expressibilities
  - They approximate the curve found in the paper
  - I have done some hyperparameter exploration
- Still to do
  - make actual plots
  - compare the output circuit performance
- Also contacted authors
  - While I think I did it correctly, I am not certain

== What's next?

- Finish up GA-QAS
- Run it overnight with different hyperparameters to collect data
- Use responses from authors to improve both
- *Add entanglement proxy to GA-QAS*
  - Also prepares for QD-QAS
- Setup framework to make QD-QAS
- Write down progress so far to pick up easier after surgery

= Week 6
The plan

== Evolutionary algorithms

High level protocol:
1. Generate a random population
2. Evaluate the fitness
3. Select the better individuals
4. Produce offspring
5. Repeat until goal reached at 2

Generally Genetic Algorithms but alternatives exist

== Genetic Algorithm

Each item in the population has genes,
these combine and mutate to produce offspring.

Assumes some kind of "building blocks"

Tends to local optimum instead of global

== Genetic Algorithms for QAS

Population tends to local optimum \
$->$ risk for circuits with similar "area" of expressibility

We want diversity in the final circuits \
$->$ probability of at least one having high expressibility in solution area

Limit offspring mutations \
$->$ Need to keep offspring within hardware constraints

== Implemented Genetic Algorithms for QAS

Applied in Arxiv submission "Genetic optimization of ansatz
expressibility for enhanced variational quantum algorithm
performance."@genetic-expressibility

Does:
- Problem agnostic QAS
- Depth limiting as noise limit

However:
- No noise simulation *or* proxy
- Maximising expressibility instead of target
- Entanglement not included at all

== What I will be doing

1. Implement Quality-Diversity evolutionary Algorithm that does sampling of the gate space
2. Hardware constraints
    - Qubit connectivity
    - Per-qubit gate types (for NV-centers etc.)
    - Scheduling constraints
3. Add more proxies
    - Entanglement
    - Noise/Fidelity
    - Trainability (maybe)
4. Test (first simulation, then hardware if possible)

= Week 5
Methods of QAS

== Training-Free QAS@training-free

#slide()[
  #align(center)[advantages]
  - Proxies help with fast filtering
  - Already uses expressibility like we want
  - Does not need training for new hardware
][
  #align(center)[disadvantages]
  - Naive algorithm
    - Random sample
    - Sort by proxy
    - Sort by 2nd proxy
    - Try optimising
  - Noise systems not included
]

== Reinforcement Learning QAS@akash

#slide()[
  #align(center)[advantages]
  - Training on evaluation directly
  - Easy constraints using _illegal actions_
  - Only needs actions and fitness function
  - Can gather its own data
  - Noise included by data gathering method
][
  #align(center)[disadvantages]
  - Needs significant time to train
  - Currently only on problem specific
    - directly on post optimisation output
]

== Graph Neural Network QAS@liu2025haqgnnhardwareawarequantumkernel

#slide()[
  #align(center)[advantages]
  - Predict instead of evaluate
    - Fidelity
    - Classification accuracy
  - fast filtering of random circuits
][
  #align(center)[disadvantages]
  - GNNs need a lot to train
  - Not directly generating good circuits
  - GNN doesn't select best qubit cluster
    - Done seperately beforehand
]

== Differentiable QAS

#slide()[
  #align(center)[advantages]
  - Allows for Gradient Descent
  - Can be tailored to specific hardware
][
  #align(center)[disadvantages]
  - Paper focussed on QAOA, don't know about others
  - Search is inherently Hamiltonian dependent
]

== Neural Predictor based QAS@npqas

#slide()[
  #align(center)[advantages]
  - circuit structure works on different qubit sizes
  - significant efficiency gains over random search
  - no parameter optimisation during search
  - uses neural nets only as filter
][
  #align(center)[disadvantages]
  - Also randomly samples circuits first like TF-QAS
  - Has to attempt $O(100)$ ansatze before finding optimal
]

== (Supernet based) QAS@supernet-qas

#slide()[
  #align(center)[advantages]
  - Unifying noise inhibition and trainability
  - No ancillary quantum resource
  - Almost identical runtime to VQA-based
  - Compatible with all platforms
  - Integrates with other methods
    - Error mitigation
    - Barren plateau resolving
][
  #align(center)[disadvantages]
  - Classical optimizer each sample
  - Choice of supernet shape
]

== Conclusion

Two main groups:
- "Building the circuit":
  Starts empty and gates are added
- "Sampling and filtering"
  Samples random circuits and uses proxies to filter

None of the QAS listed find an admissible circuit "in one shot" from what I can tell,
they all either optimise parameters as part of the search protocol or need
multiple outputs to be optimised until a good enough one is found.


== Conclusion

Likely better for us: "Sampling and Filtering"
- Allows for sampling random "hardware-allowed" circuits
- Expressibility and Entanglement are already both proxies we want to optimise
- No need to train ML for every hardware architecture/
  - Can still use ML to filter the sample, but this can be more hardware agnostic
  #text(fill: orange)[
  - Could maybe also train ML for "random" hardware architectures
    to try and make it build admissible circuits in a transferable way but this is unexplored
]

== Together Conclusion

- Sample using Evolutionary Algorithms versus Random Sampling

- Create proxy for Noise

- Improve path based proxy to be an entanglement proxy directly
  - OR machine learning some proxy that does a similar thing

== Planning

#slide[
  #align(center + horizon)[
  #cetz-canvas(length: 0.8cm, {
    import cetz.draw: *

    let lower = -10

    content((today-offset, 0), anchor: "south", [today])
    line((today-offset, -0.5), (today-offset, lower), stroke: (paint: rgb("#ff00cc")))

    for x in (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33) {
      content((x, 0), text(size: 0.4em)[#(datetime(day: 10, month: 11, year: 2025) + duration(weeks: x)).display("[day]/[month]")], anchor: "north")
      line(stroke: (paint: lime, dash: "dashed"), (x, -0.5), (x,lower))
    }


    line((3.6, -0.5), (3.6, lower), stroke: (paint: rgb("#0000dc")))
    content((5, lower - 0.1), anchor: "north", [Literature review \ of methods])

    line((6.3, -0.5), (6.3, lower), stroke: (paint: rgb("#0000dc")))
    content((6.3, lower - 2.9), anchor: "north", [Methodology \ Decision])

    line((15.2, -0.5), (15.2, lower), stroke: (paint: rgb("#ff0000")))
    content((15.2, lower - 0.1) ,anchor: "north", [Midterm])

    line((28.2, -0.5), (28.2, lower), stroke: (paint: rgb("#ff0000")))
    content((28.2, lower - 0.1) ,anchor: "north", [Greenlight])

    line((32.8, -0.5), (32.8, lower), stroke: (paint: rgb("#ff0000")))
    content((32.0, lower - 2.1), anchor: "north", [Finalisation])

    chev((7, -2), 2, f: lg(blue.lighten(20%), blue.lighten(5%)))
    content((7.5, -3.5), anchor: "north", "Holiday")


    chev((9, -2), 5.5, f: lg(green.lighten(20%), green.lighten(5%)))
    content((11.5, -4.5), anchor: "north", "Making project")

    chev((14, -7.8), 1.4, f: lg(red.lighten(20%), red.lighten(5%)))
    content((15, -5.7), anchor: "north", "Midterm Prep")

    chev((15, -2), 4, f: lg(green.lighten(20%), green.lighten(5%)))
    content((16.5, -3.5), anchor: "north", "Finish project")

    chev((19, -7), 1, f: orange)
    content((19.5, -8.3), anchor: "north", "Feature Freeze")

    chev((20, -2), 6, f: lg(green.lighten(20%), green.lighten(5%)))
    content((21.5, -4.5), anchor: "north", "Data Gathering")

    chev((22, -3), 7, f: lg(red.lighten(20%), red.lighten(5%)))
    content((25.5, -5.5), anchor: "north", "Writing")

    chev((29, -6), 2, f: lg(red.lighten(20%), red.lighten(5%)))
    content((29.5, -7.5), anchor: "north", "Review V1")

    chev((31, -2), 2, f: lg(red.lighten(20%), red.lighten(5%)))
    content((31.5, -3.5), anchor: "north", "Final Fixes")

    // chev((13, -2), 7, f: purple, offset: -3.0)
    // content((14.5, -3.5), anchor: "north", [Surgery])
  })
  ]
]

== Shuffles

The amount of shuffles where no shared neighbors before and after exist:

- 16: $131072 = 2^17$

- 17: $8454144 approx 2^23.01$

- 18: $174063616 approx 2^27.38$

- 19: ???

#image("./images/shuffles_file.jpg")

= Week 4

== Presentation

Training-Free QAS presentation #link("./tf-qas.pdf")[pdf]


= Week 3

== Outline

#align(horizon)[
Project plan

State of the Art

Planning
]

== The Plan

#slide[
  #align(center + horizon)[
  #cetz-canvas({
    import cetz.draw: *
    let left = -9
    let mid = 0
    let right = 7
    let arr_col = rgb("#00a6d6").lighten(70%)

    content((left, 6), [Inputs])
    content((mid, 6), [Process])
    content((right, 6), anchor: "west", [Outputs])

    content((left, 3), [Qubits])
    content((left, 2), [Gates])
    content((left, 1), [Connections])
    content((left, 0), text(fill: red)[Fidelities])
    content((left, -1), [Expressibility])
    content((left, -2), [Entanglement])
    content((left, -3), text(fill: red)[Noise Treshold])
    content((left, -4), text(fill: red)[Max Parameters])

    line(
      (-5.6, 0),
      (-2.1, 0),
      stroke: (
        thickness: 8pt,
        paint: arr_col,
        cap: "round",
      ),
      mark: (end: "stealth", scale: 8, fill: arr_col),
    )

    content((0,0), [test])

    rect(cetz.vector.add((mid, 0), (-2, -2)), cetz.vector.add((mid, 0), (2, 2)), radius: (rest: .4), fill: rgb("#00b3dc"))
    content((mid, 0), text(size: 4em)[?])

    line(
      (2.4, 0),
      (6.0, 0),
      stroke: (
        thickness: 8pt,
        paint: arr_col,
        cap: "round",
      ),
      mark: (end: "stealth", scale: 8, fill: arr_col),
    )

    content((right, 3), [QML Kernels], anchor: "west")
    content(cetz.vector.add((right, 2), (1, 0)), anchor: "west", [Balanced])
    content(cetz.vector.add((right, 1), (1, 0)), anchor: "west", text(fill: red)[Best Expressibility])
    content(cetz.vector.add((right, 0), (1, 0)), anchor: "west", text(fill: red)[Best Entanglement])
    content(cetz.vector.add((right, -1), (1, 0)), anchor: "west", text(fill: red)[Least Noise])
    content(cetz.vector.add((right, -2), (1, 0)), anchor: "west", text(fill: red)[Fewer Parameters])
  })
  ]
  #text(fill: red)[red] text means it's a feature to focus on once the black points work
]

== The Process

- Cost function based on
  - Expressibility
  - Entanglement
  - #text(fill: red)[Noise Treshold]
  - #text(fill: red)[Max Parameters]

- Possible Methods (not complete)
  - Monte-Carlo Tree-Search
  - Machine Learning (many options)
  - Bayesian Optimization
  - Differentiable Optimization strategies


== State-of-the-art

#slide(composer: (auto, auto))[
  #cetz-canvas({
    import cetz.draw: *

    line((0, 0.4), (0, 9), mark: (symbol: "stealth"))
    content((-3, 4.5), anchor: "south", [Hardware], angle: 90deg)
    content((-0.4, 1.0), anchor: "east", [agnostic])
    content((-0.4, 8.0), anchor: "east", [specific])

    line((0.4, 0), (9, 0), mark: (symbol: "stealth"))
    content((5, -1.4), anchor: "north", [Task])
    content((2, -0.4), anchor: "north", [agnostic])
    content((8, -0.4), anchor: "north", [specific])

    circle((1.3, 2), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Hardware-Efficient Ansatz@expressibility-and-entanglement])
    circle((1, 1), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Random circuit])
    circle((7, 1), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Unitary Coupled-Cluster \ Singles and Doubles])
    circle((9, 6), radius: 0.1, fill: black)
    content((rel: (-0.3, -0.3)), anchor: "east", text(size: 0.6em)[Reinforcement-learning \ VQE@akash])
    circle((7, 7), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Hardware-aware Quantum \ Graph Neural Network@liu2025haqgnnhardwareawarequantumkernel])
    circle((8, 5), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Supernet@supernet-qas])

    circle((1.1, 7), radius: (1, 2.0), fill: rgb(0, 90, 180).lighten(40%))
    content((1.1, 7), [Goal])
    circle((1.3, 8), radius: 0.1, fill: black)
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Training-Free Search@training-free])
  })
][
  #align(horizon)[
  Reasons for research:
  - Fast start on new problem

  - Hardware update cycle

  - Use as a starting point
  ]
]

== Comparing with training-free Search@training-free

Ways to improve:

- Smarter sampling

- Target expressibility instead of HAAR distribution

Parts to maybe re-use:

- Path-based proxy
  - Very fast
  - Approximates entanglement
  - Filter out worst circuits

- Benchmarking
  - allows for apples-to-apples



== Planning

#slide[
  #align(center + horizon)[
  #cetz-canvas(length: 0.8cm, {
    import cetz.draw: *

    let lower = -10

    content((today-offset, 0), anchor: "south", [today])
    line((today-offset, -0.5), (today-offset, lower), stroke: (paint: rgb("#ff00cc")))

    for x in (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33) {
      content((x, 0), text(size: 0.4em)[#(datetime(day: 10, month: 11, year: 2025) + duration(weeks: x)).display("[day]/[month]")], anchor: "north")
      line(stroke: (paint: lime, dash: "dashed"), (x, -0.5), (x,lower))
    }


    line((3.6, -0.5), (3.6, lower), stroke: (paint: rgb("#0000dc")))
    content((5, lower - 0.1), anchor: "north", [Literature review \ of methods])

    line((6.3, -0.5), (6.3, lower), stroke: (paint: rgb("#0000dc")))
    content((6.3, lower - 2.9), anchor: "north", [Methodology \ Decision])

    line((15.2, -0.5), (15.2, lower), stroke: (paint: rgb("#ff0000")))
    content((15.2, lower - 0.1) ,anchor: "north", [Midterm])

    line((28.2, -0.5), (28.2, lower), stroke: (paint: rgb("#ff0000")))
    content((28.2, lower - 0.1) ,anchor: "north", [Greenlight])

    line((32.8, -0.5), (32.8, lower), stroke: (paint: rgb("#ff0000")))
    content((32.0, lower - 2.1), anchor: "north", [Finalisation])



    // line((14.5, -0.5), (14.5, lower), stroke: (paint: rgb("#ff00cc")))
    // content((14, lower - 0.1), anchor: "north", "Midterm")
    //
    // chev((0.6,-2), 6.6, f: lg(yellow, yellow.darken(10%)))
    // chev((6.2,-2), 1.0, f: gradient.linear(green, rgb(0,0,0,0), angle: 60deg).sharp(3).repeat(6))
    // content((1.1,-2), anchor: "west", "Literature")
    chev((7, -2), 2, f: lg(blue.lighten(20%), blue.lighten(5%)))
    content((7.5, -3.5), anchor: "north", "Holiday")
    //
    // chev((9, -2), 6, f: lg(red, red.darken(10%)))
    // content((10, -2), anchor: "west", "Make V1")
    //
    // chev((15.5, -2), 10.5, f: lg(red, red.darken(10%)))
    // content((15.5, -1.5), anchor: "west", "Improvements")
    // content((19.5, -2.5), anchor: "west", "Testing")
    //
    // chev((15.5 + 10.5, -2), 2, f: lg(purple, purple.darken(10%)))
    // content((25.5, -3.5), anchor: "north", "Writing")

  })
  ]
]

#slide[
  == References <touying:unoutlined>
  #bibliography("references.bib", title: [])
]
