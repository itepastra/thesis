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
    content((rel: (0.3, 0)), anchor: "west", text(size: 0.6em)[Supernet@architecture-search])

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

#let chev(start, len, f: none) = {
  import cetz.draw: *
  line(fill: f,
    cetz.vector.add(start,(-1, -1))
  , cetz.vector.add(start, (len - 1, -1))
  , cetz.vector.add(start,(len, 0))
  , cetz.vector.add(start, (len - 1, 1))
  , cetz.vector.add(start,(-1,1))
  , start
  , cetz.vector.add(start,(-1,-1)))
}

#let lg(color1, color2) = gradient.linear(color2, color1, color2, angle: 90deg)

#let today-offset = (datetime.today() - datetime(day: 10, month: 11, year: 2025)).weeks()


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
