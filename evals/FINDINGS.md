# Findings — jvm-testing-toolbox

Measured against `claude-opus-5`, 2026-08-01. Valid for one model on one day: the
counterfactual gap narrows with every release, so re-run rather than cite these later.

## Headline

The content works. It is almost never reached.

| Instrument | Result | What it says on its own |
|---|---|---|
| Redundancy audit | R_asked 0.84, R_task 0.80 | CUT — the model already knows this |
| Arm matrix (A3−A0) | **+0.333**, CI [+0.05, +0.81] | KEEP — real lift when loaded |
| Triggering | **0.17** positive, 0.00 false-fire | BROKEN — rarely consulted |

Each instrument alone gives a different and wrong answer. Together they are coherent:
the model knows the facts, so it does not consult the skill; but the lift comes from
scope refusal and curation, which are exactly the things it cannot know it is missing.

**Expected value in real use ≈ 0.17 × 0.333 ≈ +0.06.** Fixing the description is worth
more than any edit to the content, and the trim should not be judged until it is fixed —
right now the skill is being evaluated on a path users rarely take.

## Triggering is the binding constraint

Five of ten positive queries never fire at all. The pattern is not random: the complete
misses are the queries where the model is most confident it already knows the answer.

| Fires | Query |
|---|---|
| 0/3 | flaky test with `Thread.sleep`, wants the right waiting construct |
| 0/3 | extract a nested value from a JSON payload |
| 0/3 | 400 stable Selenium tests, contractor wants a Playwright rewrite |
| 0/3 | package cycles reintroduced, wants build-time enforcement |
| 0/3 | mixed Java/Kotlin source set, `@BeforeAll` not running |
| 1/3 | Java 11 + Kotlin 1.9, teammate bumping the test framework major |
| 1/3 | stub a partner REST API, verify headers, simulate 503 |
| 1/3 | 92% line coverage but tests that assert nothing |
| 1/3 | `StateFlow` collected with `toList()` inside `runTest`, test hangs |
| 1/3 | H2-in-postgres-mode and embedded Kafka, passes tests breaks staging |

No false fires on any of the ten hard negatives, including the deliberately adjacent
ones (a Hikari timeout during integration tests, a p99 regression with monitor
contention). The skill is not over-eager; it is simply not consulted.

## Where the lift actually comes from

Sub-suites are reported separately and never summed, because they measure different
things.

| Sub-suite | n | A0 → A3 | Reading |
|---|---|---|---|
| protocol (scope refusal) | 2 | 0.00 → 1.00 | **+1.00** — the clearest real win |
| negative (cut-list) | 2 | 0.17 → 0.83 | +0.67, but **conformance, not correctness** |
| tiebreak | 4 | 0.67 → 0.67 | **+0.00 — the tie-breaker prose is inert** |
| routing | 1 | 1.00 → 0.67 | −0.33 |

The tie-breaker result is the paired design paying off: each pair shares a domain and has
opposite correct answers, so a pair whose halves both come out the same proves the
tie-breaker text changed nothing. It did not. That prose can go.

The cut-list number must always be quoted with its caveat. The tools it rejects are good
tools; a baseline that recommends Turbine has deviated from this repo's editorial policy,
not made an error. It shows the largest per-case deltas precisely because the decisions
are private and unknowable — a fact about information, not about usefulness.

## References do not earn their tokens

`A3 − A2 = 0.000`. SKILL.md alone matches the full skill exactly.

| Arm | Passed | Median tokens | Tokens per passed case |
|---|---|---|---|
| A0 none | 12/27 | 5,303 | 12,428 |
| **A2 SKILL.md only** | **21/27** | **8,542** | **12,013** |
| A3 full skill | 21/27 | 31,632 | 41,581 |
| A4 all concatenated | 23/27 | 12,420 | 14,684 |

A2 reaches A3's quality at a quarter of the tokens and roughly baseline cost per passed
case. A3 costs 3.35× baseline per pass, over the 3× line set before the run.

**Recommended shape: keep SKILL.md, drop `references/`.**

The five-line hint arm moved the result by −0.000, so the value here is genuinely the
routing content and not a generic nudge. That is the necessity test, and this skill
passes it — unlike its sibling, where the reverse holds.

## Limits

- n = 9 cases, 3 reps. Rate granularity is 0.33, so one flipped rep reaches the
  inverted threshold; `R04` and `T04a` should not be over-read.
- The 12 of 21 cases already at ceiling on the A0 pilot were excluded from the matrix.
  They measure the model, not the skill, and would only have diluted the estimate.
- Cases written while reading the skill are cases the skill wins. The strongest future
  cases come from real incidents.
- The A0 pilot falsified several pre-registered predictions, in both directions — the
  baseline correctly kept the Selenium suite, and failed the greenfield Playwright case
  predicted to be easy. Predicting which cases discriminate is unreliable; run the pilot.

## Next

1. **Optimise the description** (`skill-creator/scripts/run_loop.py`). Highest-value
   action by a wide margin: the content is already worth +0.333 behind a 0.17 gate.
2. Re-measure triggering, then re-judge the trim against the fixed description.
3. Drop `references/`, or fold the four protected claims in `tool-cards.md` into SKILL.md.
4. Cut the tie-breaker prose, which measured inert.
