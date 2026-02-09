# After recovery period list

Hello me, this is a list for you to get back on track with the QD-QAS you were working on...

## Things I've done

I have made baselines for two types of optimization free QAS, namely TF-QAS and GA-QAS.
These aren't necessarily fully confirmed to be functional yet,
but seem to be doing mostly the correct things. Although the TF-QAS doesn't give me the same
results as the version for the paper.
This might still need to be fixed, but could also not matter that much. // Discuss with sebastian

## What to do next

Make meetings with Sebastian and Koen!!!!!

1. Have a system to generate and work with quantum circuits
2. Create some metrics to use for the QAS
   - expressivity: how uniformly does it cover the hilbert space
   - entanglement: how many correlations exist between the qubits
   - noise: what is the fidelity of the final circuit
   - parameter count: how many parameters are in the circuit
3. Make a genetic algorithm using (some of) these metrics
4. Create a metric to estimate the "distance" between two PQCs
5. Use this distance metric to make Quality Diversity evolutionary algorithm instead
6. Compare with the baselines and normal GA with the metrics

## What is knowledge you might want to have

Expressivity is a double edged sword, too little and you won't get the result, too much
and barren plateaus will make the optimizer suffer.

Entanglement works well if the underlying problem is entangled, but can also decrease the expressivity.

Noise is just straight up bad.

More parameters is also kinda not what you want.

## A letter to me

You made a promise to Nynke that you would tell her if there were problems.
So please do that, try not to wait until they're about to blow up, as that won't help.
Sebastian and Koen also want you to succeed so if they're harsh that isn't a personal attack
as they're just trying to help you.
In general this will mean you waited too long to ask questions to them, not that you asked too many.

And above all, remember that you are enough already. You don't need to do a PhD worth of research in
6 months. That'd be insane. YOU CAN DO THIS!!!

Peppi believes in you, Nynke believes in you, your parents believe in you, I (you) believe in you.
You can do this, and if you think you can't I will bet on it.
If it's too much torture, and you barely can get yourself to work on it. Take a step back, ask people
and don't feel too bad about it. After all, it IS hard, you don't have to be able to do it all yet.
This is what learning is all about.

Yours truly,
Noa
