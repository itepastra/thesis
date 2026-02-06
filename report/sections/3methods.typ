#import "@preview/classy-tudelft-thesis:0.1.0": *
#import "@preview/physica:0.9.6": *
#import "@preview/unify:0.7.1": num, numrange, qty, qtyrange
#import "@preview/zero:0.5.0"

= Methods

In this chapter I'll go into what I made, how I made it and a bit of why I did it a certain way.
It won't be written in a chronological order.
I will start by talking about the created algorithm, after which I will explain the benchmarks,
and finally the shortly mention the algorithms@training-free@genetic-expressibility used as baselines.

== Quality-Diversity Quantum Architecture Search

== Benchmarking

As the goal of QD-QAS is to create quantum circuits that are hardware-specific but task-agnostic.
The same search outputs should be tested on multiple problems. They should be compared to the
transpiled versions of Hardware Efficient Ansatze@hea-kandala as well as other searches that don't involve
search-time optimization.

== Baseline tests

We started by implementing the protocols from Training-Free Quantum Architecture Search@training-free and
Genetic optimization of ansatz expressibility for enhanced variational quantum algorithm performance@genetic-expressibility.
So we have some related algorithms to compare our QD-QAS against.
In this section I'll go into how these implementations went.

=== Training-Free Quantum Architecture Search

As the source code wasn't linked anywhere in the paper I started by trying to replicate it purely from the texts.
But doing it this way I ran into an issue with reproducibility. This led me to contact the authors who
sent me the code very quickly. Translating their code so I could use it with the same testing as mine was
my next goal. I already had large parts the same but not all so this isn't done yet as of 06-02-2026,
but I might be able to finish later today.

=== Genetic optimization of ansatz expressibility for enhanced variational quantum algorithm performance

Like the other paper there was no link to a repository with the code, but this paper included more pseudocode
samples so I think I was able to replicate it quite quickly. I need to create some more actual benchmarks to compare
them (and mine once I make it)
