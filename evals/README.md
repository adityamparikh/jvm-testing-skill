# Evaluating this skill

Two questions, needing different instruments:

- **Does the skill help?** Outcome lift over a model with no skill loaded.
- **Is it truly needed?** Whether the content beats a five-line reminder, and whether the
  model already knows it.

The second is the one that decides whether the router earns its tokens. A skill that only
beats *nothing* has shown that a nudge helps, not that the skill is necessary.

Results are stamped with the skill SHA, model id and date. They are valid for one model on
one day — the counterfactual gap narrows as base models absorb this material, which is the
most important long-run finding for a skill like this one.

---

## Layout

```
evals/
  redundancy/claims.json   checkable claims extracted from SKILL.md + references/
  route/cases.json         20 cases across four sub-suites
  route/schema.json        forced JSON output, so scoring is exact matching
scripts/                   shared with java-performance-skill; see that repo's
                           evals/README.md for the full methodology
```

`evals/results/` and `*.checkpoint.jsonl` are gitignored.

---

## Stage 1 — redundancy audit

```bash
python3 scripts/probe_redundancy.py evals/redundancy/claims.json \
  --out evals/redundancy/results.json --runs 3 --workers 6
python3 scripts/report_redundancy.py evals/redundancy/results.json \
  --markdown evals/redundancy/report.md
```

Measures **R_asked** (knows the fact when asked) against **R_task** (reaches for it
unprompted in a realistic scenario). `references/pitfalls.md:8` claims these are "the
mistakes and decision points the base model tends to miss" — this is the test of that
claim, and it had never been run.

The gap between the two rates decides the verdict: content the model knows but does not
deploy should become a one-line reminder, not 160 lines of prose. Content it does not know
stays verbatim. `curation` claims are scored separately, because a private editorial
decision scores ~0 redundancy by construction.

Spot-audit ~10% of grader verdicts by hand before believing the table.

---

## Stage 2 — the route suite

```bash
python3 scripts/run_arms.py evals/route/cases.json \
  --schema evals/route/schema.json \
  --skill-dir .claude/skills/jvm-testing-toolbox \
  --arms A0:5,A3:5 --out evals/results/$(date -u +%Y%m%dT%H%M)
```

Four sub-suites, **reported separately and never summed**, because they measure genuinely
different things:

| Sub-suite | n | Measures |
|---|---|---|
| `routing` | 5 | Correctness — one case per table row, matched against the bold default |
| `tiebreak` | 8 (4 pairs) | Whether the tie-breaker prose does any work |
| `negative` | 3 | **Conformance to this repo's editorial policy, not correctness** |
| `protocol` | 5 | The two behaviours `SKILL.md` claims about itself |

**Tie-breaker pairs** share a domain and have opposite answers — "400 stable Selenium
tests, add one flow" versus "greenfield, no browser tests". A pair whose halves get the
same answer proves that tie-breaker text is inert and should be cut. Only the pair carries
information; neither half alone does.

**The negative sub-suite needs its caveat printed next to its number, every time.** The
cut tools in `README.md:120-133` are good tools. A baseline that recommends Turbine has
made a policy deviation, not a mistake. This sub-suite will show the largest delta in the
whole study precisely because the decisions are private and unknowable — that is a fact
about information, not about usefulness.

**Protocol** tests the scope-refusal rule (`SKILL.md:41-42`) and the currency rule
(`SKILL.md:44-51`). P05 is the over-refusal control: an on-map question that must *not* be
refused, because refusing is only a win when the refusal is correct.

Testcontainers and Playwright cases exist in `routing` only. Docker is unavailable in this
environment, so they cannot be execution-verified — stated here rather than silently
omitted.

---

## Scoring notes

Scoring is mechanical — exact matching on forced JSON fields, no model grading another
model. Two refinements were forced by real failures:

- **A synonym map**, because `JUnit 6 (Jupiter)`, `JUnit 6` and `Jupiter 6` are the same
  answer and a scorer that distinguishes them measures phrasing, not routing.
- **Cut-list checks match the tool actually recommended**, after normalisation, not any
  substring. An answer of "JUnit Jupiter, optionally with kotest-assertions-core" was
  being failed for containing "kotest" — but the assertions module needs no second
  Platform engine, so it does not breach the one-engine rule the cut list exists to
  protect. A case key may therefore also name a *set* of acceptable answers.

Both are instances of the same lesson: substring matching keeps failing nuanced correct
answers, always in the direction that flatters whichever arm is blunter.

---

## First signal

From the initial smoke test, one run per arm on P01 (a load-testing question, explicitly
out of scope per `README.md:124`):

| Arm | Answer | |
|---|---|---|
| A0 no skill | `tool: "Gatling"`, `off_map: false` | fail — confidently routes off-map |
| A3 full skill | `tool: ""`, `off_map: true` | pass |

Exactly the predicted split, on a behaviour the skill claims about itself and that nothing
had previously verified. One run per arm proves nothing on its own — but it does show the
assertion discriminates, which is the property most eval assertions lack.
