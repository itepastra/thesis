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


// References displayed like [1], [2] and captions to images
// Introduction


#title-slide()

#show outline.entry: it => link(
  it.element.location(),
   text(fill: rgb("#00b3dc"), size: 1.3em)[#it.indented(it.prefix(), it.body())],
)


#outline(depth: 1, title: text(fill: rgb("#00a6d6"))[Content])

=

== Context

- VQE for NISQ
- Ansatz $->$ big effect
- QAS to optimize
  - noise
  - parameters

== Research Question

#align(center + horizon)[
  _
  How can hardware knowledge about noise, connectivity and native gates
  be used to improve the performance of Quantum Architecture Search 
  for Variational Quantum Eigensolvers?
  _
]

== Planning

#let chev(start, len, f: none) = {
  import cetz.draw: *
  line(fill: f,
    cetz.vector.add(start,(-1 , -1))
  , cetz.vector.add(start, (len - 1, -1))
  , cetz.vector.add(start,(len, 0))
  , cetz.vector.add(start, (len - 1, 1))
  , cetz.vector.add(start,(-1,1))
  , start
  , cetz.vector.add(start,(-1,-1)))
}

#let lg(color1, color2) = gradient.linear(color2, color1, color2, angle: 90deg)

#slide[
  #cetz-canvas({
    import cetz.draw: *

    content((1, 0.1), anchor: "south", [today])

    for x in (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24) {
      content((x, 0), text(size: 12pt)[#(datetime(day: 10, month: 11, year: 2025) + duration(weeks: x)).display("[day]/[month]")], anchor: "north")
      line(stroke: (paint: lime, dash: "dashed"), (x, -0.5), (x,-5))
    }
    line((1, -0.5), (1, -5), stroke: (paint: rgb("#ff00cc")))

    // yellow = literature
    // green = planning
    // blue = free
    // red = make thing
    line((5.5, -0.5), (5.5, -5), stroke: (paint: rgb("#ff00cc")))
    content((5.0, -5.1), anchor: "north", "Introduction")

    line((14.5, -0.5), (14.5, -5), stroke: (paint: rgb("#ff00cc")))
    content((14, -5.1), anchor: "north", "Midterm")

    chev((0.6,-2), 6.6, f: lg(yellow, yellow.darken(10%)))
    chev((6.2,-2), 1.0, f: gradient.linear(green, rgb(0,0,0,0), angle: 60deg).sharp(3).repeat(6))
    content((1.1,-2), anchor: "west", "Literature")
    chev((7, -2), 2, f: lg(blue.lighten(20%), blue.lighten(5%)))
    content((7, -3.5), anchor: "north", "Holiday")

    chev((9, -2), 6, f: lg(red, red.darken(10%)))
    content((10, -2), anchor: "west", "Make V1")

    chev((15.5, -2), 10.5, f: lg(red, red.darken(10%)))
    content((15.5, -1.5), anchor: "west", "Improvements")
    content((19.5, -2.5), anchor: "west", "Testing")

    chev((15.5 + 10.5, -2), 2, f: lg(purple, purple.darken(10%)))
    content((25.5, -3.5), anchor: "north", "Writing")
  })

]
