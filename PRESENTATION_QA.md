# Network Reliability Monte Carlo Visualizer (+ Monte Carlo π Approximation)

This document anticipates questions that classmates/instructors are likely to ask during a project presentation of this repository.
It is written **as if you (the presenter) are being questioned by the audience**.

---

## How to use this file
- **Questions** are listed first (numbered).
- **Answers** are at the end, also **numbered to match** the questions.

---

## Questions (most likely during a class presentation)

### A. Project goals / big picture
1. What problem is this project solving, in one sentence?
2. What does “network reliability” mean in this project?
3. Why did you choose Monte Carlo simulation instead of an exact (closed-form) reliability calculation?
4. What are the two simulations in the app, and why are they in the same Streamlit project?
5. What’s the main takeaway a student should learn after using the app for 2–3 minutes?

### B. Demo / user workflow (Streamlit)
6. How do you run the app locally?
7. What controls can the user adjust in “Network Reliability” mode?
8. What controls can the user adjust in “Approximating Pi” mode?
9. Why does the app sometimes show a warning that the configuration changed?
10. What does the “Reliability Curve” plot represent?
11. What is the “Simulate One Trial (Animated)” feature intended to teach?

### C. Graph types and what they imply
12. What graph types can be generated, and what do they represent intuitively?
13. For a **tree**, can you predict the reliability shape without simulation?
14. For a **cycle graph**, what failure patterns disconnect it?
15. For a **complete graph**, why is it so reliable for small-to-moderate failure probabilities?
16. What is the “Degree-Constrained Graph (3 ≤ deg ≤ n−2)” option, and why is it interesting?
17. Are the generated graphs deterministic or random between runs?
18. Why use a spring layout, and is the layout part of the math or just visualization?

### D. Monte Carlo method details (network reliability)
19. What is the random model of failures (exactly what fails and with what probability)?
20. What does the parameter **q** mean, and what happens when q = 0 or q = 1?
21. What does “trial” mean in the Monte Carlo simulation?
22. What is the estimator for reliability used here?
23. What are the sources of randomness in the results?
24. How accurate is the Monte Carlo estimate (how do you reason about error bars / confidence intervals)?
25. How many trials do you need to get “good enough” results?
26. Is the simulation unbiased?
27. What is the computational complexity per trial?
28. How does graph size (n) affect runtime?
29. Why cap the reliability-curve trials to `min(n_trials, 50)`?
30. Why do you cache some functions, and what does that change?
31. Does caching risk returning stale or incorrect results?

### E. Theoretical concepts referenced (bridges, min-cut, bounds)
32. What is a **bridge** (cut-edge) and why does it matter for reliability?
33. Why are bridges highlighted in red in the graph visualization?
34. Can you explain the bound mentioned in the README: “(1−q)^k reliability bound”?
35. What is a **minimum cut** (λ), and why is it theoretically linked to reliability for small q?
36. Does the current code actually compute min-cut (λ)? If not, why mention it?
37. If you were to add a min-cut computation, where would it fit in the UI?

### F. π approximation page (why it works)
38. How does the dartboard (square + circle) simulation estimate π?
39. Why is π approximately `4 * hits / total`?
40. What assumptions are required for this method to work?
41. What does the convergence plot demonstrate?
42. Why does the estimate bounce around early and stabilize later?
43. Why simulate in batches with a short sleep?
44. Is the π simulation “real-time” Monte Carlo or precomputed then animated?

### G. Validation / sanity checks
45. How did you validate that the reliability results make sense?
46. What are some known expected outcomes (e.g., tree reliability, extreme q values) that you can check live?
47. How do you know the animation corresponds to the same model used in the Monte Carlo estimate?
48. Did you compare any results to theoretical values for small graphs?

### H. Engineering / software design
49. Why build this as a Streamlit app instead of a script or notebook?
50. How is the code structured at a high level?
51. What libraries are used and why?
52. How do you ensure the app stays responsive while simulating?
53. What are the current limitations of the implementation?
54. What would you refactor first if you had more time?
55. How would you make results reproducible (same random output every time)?

### I. Edge cases / correctness concerns
56. What happens if edges are removed until the graph becomes disconnected—does the code handle it safely?
57. Could `nx.is_connected` throw errors (e.g., empty graph), and do you guard against that?
58. Does the “degree-constrained graph” generator always terminate?
59. What happens for very small n (like n=3 or n=4) in the degree-constrained option?
60. Are there any cases where the reliability curve could look “wrong” due to too few trials?

### J. Performance / scalability
61. What is the slowest part of the program?
62. What would you do to speed it up for larger graphs or more trials?
63. Why not vectorize or use NumPy for the network reliability simulation?
64. Could you parallelize trials, and what would be the easiest approach in Python?
65. Why not compute exact reliability using inclusion–exclusion or state enumeration?

### K. Interpretation / discussion questions
66. If two graphs have the same number of nodes and edges, can their reliability differ? Why?
67. Why is “minimum degree” not a complete predictor of reliability?
68. How do bridges and min-cuts relate to “weak points” in a network?
69. What real-world systems might be modeled by this kind of edge-failure reliability?
70. If edges had different failure probabilities, how would the model and code change?
71. If nodes (not edges) could fail, how would the model change?
72. What if failures were correlated (not independent)?

### L. Presentation / project-management
73. What did each team role contribute (math vs computational lead) according to the README?
74. What was the hardest part: theory, coding, or visualization?
75. If you had to summarize in 30 seconds, what would you say?
76. If we repeated your experiment tomorrow, would we get the exact same curves/results?

---

## Answers (numbered to match)

1. The project estimates **how likely a network stays connected** when edges randomly fail, and visualizes how structure impacts robustness.
2. Here, “network reliability” is the **probability that the graph remains connected** after each edge independently fails with probability **q**.
3. Exact reliability quickly becomes computationally expensive (#P-hard in general). Monte Carlo gives a practical estimate that scales to larger graphs and supports interactive visualization.
4. Page 1: **Network Reliability** (connectivity under edge failures). Page 2: **Approximating π** (classic Monte Carlo demo). They’re together to show Monte Carlo ideas in both a geometric and graph context.
5. Graph structure (bridges, redundancy, connectivity) strongly affects robustness; Monte Carlo can approximate reliability and reveal trends like “reliability drops as q increases.”

6. Install dependencies and run Streamlit:
   - `pip install -r requirements.txt`
   - `streamlit run app.py`
7. You can choose graph type (Tree/Cycle/Complete/Degree-constrained), number of nodes **n**, edge failure probability **q**, and number of trials.
8. You choose the number of darts (samples) and run the Monte Carlo “dartboard” simulation.
9. Results are stored in `st.session_state`. If you change parameters after running, the app warns you the displayed results correspond to an older configuration until you rerun.
10. It plots estimated reliability versus q for q in `{0, 0.1, …, 1.0}` using repeated Monte Carlo estimates.
11. It gives intuition: you watch edges fail and immediately see how components split, linking the probability model to visible disconnection events.

12. Tree: minimal edges, no redundancy. Cycle: one loop redundancy. Complete: maximum redundancy. Degree-constrained: “medium-dense but not extreme” graphs that avoid very low/high degrees.
13. Yes. A tree becomes disconnected if **any edge fails**, so reliability is approximately `(1-q)^(n-1)` because a tree has `n−1` edges.
14. A cycle disconnects if you remove **2 or more** edges in a way that breaks the loop into separate components (in an n-cycle, any two distinct removed edges disconnect it).
15. Complete graphs have many alternate paths; removing a few edges rarely disconnects because there are many redundant routes between node pairs.
16. It samples connected Erdős–Rényi graphs and keeps only those whose degrees satisfy `3 ≤ deg(v) ≤ n−2`. This avoids fragile low-degree nodes and avoids being “almost complete.”
17. Tree graphs are randomly generated (labeled random tree). Degree-constrained graphs are random search. Cycle/complete are deterministic for fixed n.
18. Spring layout is for readability (aesthetic stable placement). It doesn’t change the math because connectivity depends only on edges/nodes, not drawing.

19. Independent edge failures: for each edge `(u,v)`, remove it with probability q during a trial.
20. q is **probability an edge fails**. If q=0, no edges fail → reliability 1 (if graph is connected). If q=1, all edges fail → disconnected unless n≤1 (not the case here), so reliability ~0.
21. One trial = create a copy of the graph with edges randomly removed according to q, then check if the resulting graph is connected.
22. Reliability estimate `R_hat = (# connected trials) / (total trials)`.
23. Randomness comes from (a) random edge failures per trial, and also (b) random graph generation for some graph types.
24. If you treat each trial as a Bernoulli(connected) outcome, the standard error is about `sqrt(R(1-R)/T)` for T trials, so error shrinks like `1/sqrt(T)`.
25. Depends on desired precision. Roughly, to halve noise you need 4× more trials. For classroom demos, 100–1000 trials is usually sufficient to see trends.
26. Yes, it’s an unbiased estimator of the true reliability under the independent-edge-failure model.
27. Per trial you may inspect/remove each edge: `O(m)` operations, plus connectivity check typically `O(n+m)`. So around `O(n+m)` per trial.
28. Larger n usually means more edges (depending on graph type) and more expensive connectivity checks, so runtime grows with both n and trials.
29. The curve requires running the simulation 11 times (for 11 q values). Limiting to 50 trials keeps the UI responsive while still showing the qualitative shape.
30. Caching avoids recomputing identical simulations/graphs when inputs haven’t changed, reducing flicker and speeding up reruns.
31. Caching is keyed by inputs; if inputs match, returning the cached result is correct. Staleness only happens if you expect new random values despite identical inputs—then you would disable caching or include a seed as an input.

32. A bridge is an edge whose removal increases the number of connected components. If a bridge fails, the network must disconnect.
33. Highlighting bridges shows “single points of failure” visually—edges that carry all connectivity between parts of the network.
34. If there are k bridges and all must survive for connectivity, then reliability is at most (or in a tree, exactly) `(1-q)^k` because each bridge survives with probability `(1-q)`.
35. The minimum cut size λ is the smallest number of edges whose removal disconnects the graph. For small q, the most likely disconnection events involve the smallest cuts, so failure probability often scales like a constant times `q^λ`.
36. In the current `app.py`, bridges are computed (`nx.bridges`), but a min-cut computation is **not implemented** in the visible code. It’s mentioned as theory/future extension.
37. A natural place is in the results sidebar/metrics: display λ using `nx.edge_connectivity(G)` (or a min-cut algorithm) and relate it to robustness.

38. Sample points uniformly in the square `[-1,1]×[-1,1]`. The fraction that land inside the unit circle approximates the area ratio.
39. Area(circle)=π·1²=π and area(square)=4, so `P(inside)=π/4` and π ≈ `4 * hits/total`.
40. You need uniform random sampling and enough independent samples (law of large numbers).
41. It shows the estimate approaching π as samples increase and illustrates variance decreasing with more trials.
42. Early on, each new point changes the ratio a lot (high variance). As n grows, each point has smaller marginal impact.
43. Batching + sleep creates an animation effect so viewers can watch convergence rather than instantly seeing final results.
44. The code precomputes the random points once (cached), then animates by revealing them in batches.

45. We sanity-check against known cases: q=0 should give ~1, q=1 should give ~0, and trees should follow `(1-q)^(n-1)` closely.
46. Examples: Tree with n=8 has edges=7; at q=0.1, expected reliability around (0.9)^7≈0.478. Complete graphs should remain high for small q.
47. Both use the same “remove each edge with probability q” logic; the animation just performs it once and shows intermediate steps.
48. For small graphs (small n), you can compare Monte Carlo with theoretical reasoning (tree exact, cycle near-exact via combinatorics) to verify trends.

49. Streamlit makes the project interactive for a live demo without requiring the audience to read code or run notebooks.
50. It’s a single `app.py` with two pages routed by a sidebar radio. Core tasks: generate graph → run Monte Carlo → plot metrics/figures.
51. `streamlit` (UI), `networkx` (graphs/connectivity/bridges), `numpy` (sampling/arrays), `matplotlib` (plots).
52. The network simulation uses a progress bar and runs in chunks; the curve uses fewer trials; caching reduces repeated work.
53. Limitations include: results aren’t seeded/reproducible by default; min-cut is not implemented in code; Monte Carlo can be slow for very large trial counts; degree-constrained generator can be slow.
54. Separate logic into modules (simulation, plotting, UI), add seeding and confidence intervals, and implement min-cut/edge-connectivity metrics.
55. Add an explicit random seed control and use it for Python `random` and NumPy RNG (and potentially for graph generation), then include seed in cached function keys.

56. Yes—connectivity is checked on the resulting graph after removals. As long as the graph still has the same node set, `nx.is_connected` is defined.
57. `nx.is_connected` requires at least 1 node and a graph object. Here nodes are always added (`add_nodes_from(range(n_nodes))`), so it’s safe.
58. Not guaranteed theoretically; it loops until it finds a connected graph with degree constraints. For some n it may take many attempts.
59. For n<5, the code returns a complete graph immediately to avoid impossible constraints (since you can’t have min degree 3 with n=4 in a simple graph).
60. Yes—Monte Carlo noise. With too few trials, the curve may not be monotone or may look jagged. Increasing trials smooths it.

61. Repeating many trials where each trial copies the graph and runs connectivity checks is the dominant cost.
62. Speed-ups: avoid copying graphs per trial (simulate edge survival masks), use faster connectivity (Union-Find), pre-generate random numbers, parallelize trials, or reduce repeated plotting.
63. The state is a graph connectivity problem, not just arithmetic; vectorization is less direct than in the π simulation.
64. Yes. Easiest: multiprocessing / joblib to distribute trials; or run batches in parallel and aggregate connected counts.
65. Exact reliability scales poorly because you’d need to consider many edge-up/edge-down states (2^m in the worst case).

66. Yes. Reliability depends on *where* edges are, not just how many. A graph with a bridge can be much less reliable than one without, even with the same m.
67. Minimum degree helps but doesn’t capture global structure (e.g., bottlenecks/cuts). Two graphs can have the same minimum degree but different cut sizes and redundancy patterns.
68. Bridges are cut-size 1 bottlenecks; min-cuts generalize that to the smallest bottleneck size. Both identify the “easiest” ways to disconnect the network.
69. Transportation, communication networks, power grids (simplified), social networks—any system where links can fail independently.
70. You’d assign each edge its own q(u,v) and remove edges with that probability instead of a single global q.
71. Node failures would remove vertices (and incident edges), then you’d test connectivity of the remaining induced graph.
72. Correlated failures require a different sampling model (e.g., shared risk groups, spatial outages), not independent Bernoulli per edge.

73. The README describes a **Math Lead** (theory, proofs) and a **Computational Lead** (simulation, visualization). This app is the computational component.
74. Common tough parts are balancing runtime with interactivity, and translating theory (cuts/bridges) into intuitive visual explanations.
75. “We built an interactive Monte Carlo app that shows how different graph structures stay connected under random edge failures, and we also include a π Monte Carlo demo to teach the underlying simulation idea.”

76. Not necessarily—without a fixed random seed, randomness will change exact numbers, but trends should be consistent with enough trials.
