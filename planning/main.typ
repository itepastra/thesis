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

The current title I'm using is: ....

My name is Noa Puk Aarts, and my student number is 6292755.

The project is done as part of the .... research group.

My responsible supervisor is Sebastian Feld,
and my daily supervisor is Koen Mesman.

The date of submission is #datetime.today().display()

= Introduction


= Research Question

What is a way to generate an ansatz for a specific quantum computer to perform well on variational quantum eigensolvers?

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

While there are many risks I can think of, these four seem the most likely.
I based this likelyhood on self-knowledge and my experiences with my bachelor thesis/team projects.

== Surgery pulls me out of it

I will very likely have a surgery somewhere in the spring, afterwards I'll have a revalidation period.
Since I won't be rushing my own health this may take quite a while where I won't be focusing on the project
as much. The risk is that after this I have to figure out where I was with my project and how to continue it.

Since I will know at least a couple of weeks before the surgery, I have time to wrap up the thing I'm working on
at that moment. I can also write down a short summary of what I was working on and what the next steps should be.
Once I finished (part of) my recovery I will then be able to read this summary to get back into the flow of research.

== Losing data

Because I'm using a local Git server, there is the risk of my drive failing/getting corrupted and me losing my
progress and data.

I think the chances of this happening are small but non-zero. I also
work on both my laptop and my computer which helps because I'll have somewhat recent clones of the git repository
on both. This means that three copies exist, they aren't in different locations though. But if my house burns down
I think I have bigger problems than the lost data.

== Losing Motivation

I am a person who is very bad at doing things when I'm not motivated to do them. This is partially due to
the combination of ASS and ADHD (combined type).

My motivation for this project is mostly driven from a sense to help my daily supervisor, together with
me wanting to "make something I'm proud of". I think that once I have a plan around the holidays I will
also get the new motivation source of "ooh, this is cool, I want to make this" which I hope will
last till at least the bulk of the project is done.

For the writing of the report I'm more scared, but I hope that starting with writing during the earlier
phases so that I have at least a basis will help counteract my dislike of (academic) writing.
I also have medication for my ADHD that should help with working on aspects that I know I have to do even
though I don't like them.

== Scope Creep

While working on the project I will be thinking of ways to expand the scope to cover more usecases or
changing large components due to new insights. While a small amount of this is healthy and expected,
there is a risk of it becoming too much.

To counteract the effects of scope-creep I'll be creating concrete and testable success criteria with
my supervisor. This way I can ask for ideas "is this in the success criteria?" and create a more informed
decision about if I should continue on this idea.

= Supervision plan

My responsible supervisor is, as mentioned before in @s1 Sebastian Feld.
Also mentioned before my daily supervisor is Koen Mesman.



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
  week(4), [Review Literature],
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

