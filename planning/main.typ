#import "@preview/ilm:1.4.1": *


#set text(lang: "en")

#show: ilm.with(
  title: [MEP project proposal],
  author: "Noa Puk Aarts",
  date: datetime.today(),
  bibliography: bibliography("references.bib"),
  figure-index: (enabled: true),
  table-index: (enabled: true),
  listing-index: (enabled: true)
)


= Personal Data <s1>

The current title I'm using is: Hardware Topology Inspired Quantum Ansatz Design

My name is Noa Puk Aarts, and my student number is 6292755.

The project is done as part of the Quantum Machine Learning research group.

My responsible supervisor is Sebastian Feld,
and my daily supervisor is Koen Mesman.

The date of submission is #datetime.today().display()

= Introduction

I feel like Koen wrote a good introduction on my thesis when he wrote a research proposal for me,
after meeting we decided to include that as an introduction.

== Context

Currently, Quantum Machine learning is an upcoming field, with shown advantages in data requirements for
learning from complex quantum information@quantum-advantage-bounds@quantum-advantage-learning. Currently, the quantum circuits (Ansatze) that act as
machine learning kernels are constructed using heuristics. These heuristic Ansatze are designed to have low
requirements on quantum hardware, as the current quantum computers are prone to noise and of small scale
(also dubbed the NISQ era).
The fallacy of these hardware-efficient Ansatze is that their effectiveness is not well understood. Ansatze
can be evaluated by their expressivity@expressibility-and-entanglement, i.e., how much of the Hilbert space they can explore, and their
entanglement capabilities@expressibility-and-entanglement@quantum-dynamics-physical-resource. Simply taking the expressivity is unfortunately not enough to fully capture the
Ansatze’s expected performance@expressibility-and-entanglement@scaling-variational-circuit-depth. As such, designing QML Ansatze is a non-trivial challenge.

== Scope and Motivation

The scope for this project will be the automatic design of a QML Ansatze, based on quantum hardware noise
and connectivity topology, given a set of targets. The motivation is to find quantum kernels most resilient to
the hardware noise experienced in implementation. A downside of using topology-inspired kernels is the lack
of re-usability, as it’s performance will be directly correlated to the hardware it is run on. However, it must be
noted that quantum hardware is showing increasing uniformity in its design, and (elements of) hardware are
very likely to be reused by other consumers (or can be intentionally targeted). When considering commercial
or research usage, generally, one or a few topologies are used by the user in the first place.
The proposed method is to use user defined criteria, such as expressivity, entanglement (e.g., Schmidt
strength@quantum-dynamics-physical-resource), and number of trainable parameters as a cost function, and generating an Ansatz to best fulfill
the requirement given a topology. Methods of generating the Ansatz can be done either by procedural generation
(algorithmic), using optimization methods such as genetic algorithms@architecture-search@evolutionary-architecture-search, or by using machine learning
methods such as generative AI@generative-quantum-eigensolver. The choice is to be determined by the MSc. student, based on a review of
methods.
Targets for the projects are comparisons on standard benchmarks of the QML Ansatz using hardware
simulations. If time and resources allow, this can be extended to real hardware experiments. Alternatively,
the proposed method can be further fine-tuned for more complex environments, such as resilience to time-dependency@calibration-aware-transpilation.
The novelty of this project is the bottom-up approach with great detail, exploiting NISQ hardware to its
fullest. This has to date not been shown to this extend

= Research Question

= Hypothesis

= Data Management

I will be using Git to track all the changes I've made to the report and the project.
It will start out being hosted on my personal forgejo instance, later on I will create a mirror to github.

For data from various benchmarks and other testing results I plan to include them on the git project.
If this data ends up becoming too much I can consider alternatives, but I don't expect this becomes a problem.

= Training

The Applied Quantum Algorithms course (WI4650) has introduced me to various aspects of the VQE. I'm also taking the
Quantum Computing and Quantum Programming course at the time of writing which should help as well
and should be finished near the end of january.

I also have a lot of experience programming from my gap year where it was a big hobby of mine, as well as a part-time job.
This experience will be useful since my project will have a significant focus on programming.

= Risk Management

Due to the nature of making something new, there are a couple of risks in the time management.
If, after the literature research, I decide to use a certain strategy and figure out that it won't work
much later on this could lead to a significant amount of wasted time.

To manage this risk I will define certain components which each have to work on their own before continuing.
Choosing these components carefully allows them to be interchanged when a different strategy is chosen
at a later time. This interchangability limits time spent when a direction is found fruitless.

There are also personal risks associated with me working on a project. Since I have a surgery somewhere
next year this will lead to a (possibly lengthy) revalidation period during my thesis project.
After this period I'll have to be able to hop back into the project, to help me do this I will try to
finish a contained part before the surgery and write down what the next steps in the research are.
This way I can read the next steps once I'm ready to start working again.

To limit the risks associated to scope-creep I will be making concrete steps and criteria. These
will help when I have new ideas, since I can ask if it's truly necessary or should wait till later.

= Supervision plan

My responsible supervisor is, as mentioned before in @s1 Sebastian Feld.
Also mentioned before my daily supervisor is Koen Mesman.

I am meeting with my daily supervisor every week, and we're inviting the responsible supervisor
to join as well. Depending on his ...


= Project Planning

#let kickoff-day = datetime(day: 10, month:11, year:2025)
#let week(offset) = [#(kickoff-day + duration(weeks: offset)).display("[month]/[day]") - #(kickoff-day + duration(weeks: offset, days: 6)).display("[month]/[day]")]

#table(
  columns: (auto, auto),
  table.header([*Week* (mm/dd)], [*Task*]),
  week(0), [Kick-Off],
  week(1), [Review Literature],
  week(2), [Review Literature],
  week(3), [Review Literature],
  week(4), [Review Literature], // written introduction
  week(5), [Plan project direction],
  week(6), [Holiday],
  week(7), [Holiday],
  week(8), [Start Project implementation],
  week(9), [Work on Project],
  week(10), [Work on Project],
  week(11), [Work on Project],
  week(12), [Work on Project],
  week(13), [Work on Project],
  week(14), [Create progress report],
  week(15), [Midterm],
  week(16), [Benchmarking],
  week(17), [Implement Project Improvements],
  week(18), [Implement Project Improvements],
  week(19), [Benchmarking],
  week(20), [Implement Project Improvements],
  week(21), [Implement Project Improvements],
  week(22), [Testing with hardware],
  week(23), [Implement issue fixes],
  week(24), [Testing on hardware],
  week(25), [Write Report],
  week(26), [Write Report],
  week(27), [Draft 1],
  week(28), [Green Light],
  week(29), [Write Report],
  week(30), [Draft 2],
  week(31), [Write Report],
  week(32), [Final version],
  week(33), [],
  week(34), [Help Organise Festival],
  week(35), [Help Organise Festival],
  week(36), [Help Organise Festival],
)

