#!/usr/bin/env python3
"""Turn arm runs into an honest verdict.

Three things this does that a naive mean over runs does not:

1. **Aggregates to the case before comparing.** Runs within a case share an
   artifact and a difficulty, so they are correlated. Treating 70 runs as 70
   independent observations overstates precision by roughly 2-3x and turns
   noise into significance.

2. **Bootstraps over cases, not runs.** The uncertainty that matters is "would
   a different set of cases have given a different answer", and resampling runs
   cannot see that.

3. **Classifies every case by where it sits**, because the mean hides the shape.
   A +0.20 delta from three cases swinging with eleven ties is a different
   finding from +0.20 spread evenly, and only one of them generalises.

Ceiling cases - both arms near-perfect - are counted and excluded from the
headline. They measure the model, not the skill, and leaving them in drags every
delta toward zero. Inverted cases, where the skill does WORSE than nothing, are
surfaced separately: they are the most actionable thing in any eval and averaging
buries them.

Usage:
    python scripts/analyze_arms.py evals/results/<run>/runs.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

CEILING = 0.9
FLOOR = 0.1
DISCRIMINATING = 0.3
# A regression has to clear this to be called "inverted". At 3-5 reps the rate
# granularity is 0.2-0.33, so a single flipped rep already moves a case by more
# than a rounding error. Flagging that as "the skill actively hurts" would bury
# the real regressions in noise, and this label is the one that gets acted on.
INVERTED = 0.25
PLAUSIBILITY_WEIGHT = {"common": 3, "occasional": 2, "rare": 1}


def per_case_rates(runs: list[dict]) -> dict[str, dict[str, float]]:
    """case_id -> arm -> pass rate, over runs that actually produced an answer.

    Errored runs are DROPPED, not counted as failures. A run that exited non-zero
    measured nothing, and scoring it as a miss turns infrastructure flakiness into
    a result. That matters more than it sounds: error rates are not uniform across
    arms, so the arm that happened to fail least looks best. A diagnose matrix run
    at high concurrency lost 71% of its runs this way and produced a confident,
    entirely spurious "the five-line hint is the only thing that helps".
    """
    buckets: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for run in runs:
        if run.get("error") or not run.get("answered", True):
            continue
        buckets[run["case_id"]][run["arm"]].append(bool(run.get("passed")))
    return {
        case: {arm: sum(v) / len(v) for arm, v in arms.items() if v}
        for case, arms in buckets.items()
    }


def error_audit(runs: list[dict]) -> dict:
    """Errors per arm. Uneven rates bias the comparison; report them loudly."""
    tot: dict[str, int] = defaultdict(int)
    bad: dict[str, int] = defaultdict(int)
    for run in runs:
        tot[run["arm"]] += 1
        if run.get("error") or not run.get("answered", True):
            bad[run["arm"]] += 1
    per_arm = {a: {"runs": tot[a], "errored": bad[a], "rate": round(bad[a] / tot[a], 3)}
               for a in sorted(tot)}
    overall = sum(bad.values()) / sum(tot.values()) if tot else 0.0
    rates = [v["rate"] for v in per_arm.values()]
    return {
        "per_arm": per_arm,
        "overall_rate": round(overall, 3),
        "spread_across_arms": round(max(rates) - min(rates), 3) if rates else 0.0,
        "trustworthy": bool(overall <= 0.15 and (max(rates) - min(rates) if rates else 0) <= 0.10),
    }


def bootstrap_ci(deltas: list[float], draws: int, seed: int) -> tuple[float, float]:
    """Percentile CI by resampling CASES with replacement."""
    if len(deltas) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = []
    for _ in range(draws):
        sample = [deltas[rng.randrange(len(deltas))] for _ in deltas]
        means.append(sum(sample) / len(sample))
    means.sort()
    return (means[int(0.025 * draws)], means[int(0.975 * draws)])


def classify(p_base: float, p_test: float) -> str:
    """Order matters here.

    Ceiling and floor are checked before inverted, because a case where both
    arms are near-perfect is a case that cannot discriminate - and calling a
    1.0-vs-0.8 pair "the skill is actively hurting" turns one flipped rep into
    the loudest finding in the report. Inverted then needs a real magnitude for
    the same reason.
    """
    if p_base >= CEILING and p_test >= CEILING:
        return "ceiling"
    if p_base <= FLOOR and p_test <= FLOOR:
        return "floor"
    if p_base - p_test >= INVERTED:
        return "inverted"
    if p_test - p_base >= DISCRIMINATING:
        return "discriminating"
    return "weak"


def contrast(rates: dict, cases: dict, base: str, test: str, draws: int, seed: int) -> dict | None:
    paired = [(cid, r[base], r[test]) for cid, r in rates.items() if base in r and test in r]
    if not paired:
        return None

    classes = {cid: classify(b, t) for cid, b, t in paired}
    deltas_all = [t - b for _, b, t in paired]
    non_ceiling = [(cid, b, t) for cid, b, t in paired if classes[cid] != "ceiling"]
    deltas_nc = [t - b for _, b, t in non_ceiling]

    wins = sum(1 for _, b, t in paired if t > b)
    losses = sum(1 for _, b, t in paired if t < b)
    ties = len(paired) - wins - losses

    weighted_num = sum(
        PLAUSIBILITY_WEIGHT.get(cases.get(cid, {}).get("plausibility", "occasional"), 2) * (t - b)
        for cid, b, t in paired)
    weighted_den = sum(
        PLAUSIBILITY_WEIGHT.get(cases.get(cid, {}).get("plausibility", "occasional"), 2)
        for cid, _, _ in paired)

    lo, hi = bootstrap_ci(deltas_nc or deltas_all, draws, seed)
    return {
        "contrast": f"{test} - {base}",
        "n_cases": len(paired),
        "mean_base": round(statistics.mean(b for _, b, _ in paired), 3),
        "mean_test": round(statistics.mean(t for _, _, t in paired), 3),
        "delta_all": round(statistics.mean(deltas_all), 3),
        "delta_excl_ceiling": round(statistics.mean(deltas_nc), 3) if deltas_nc else None,
        "ci95": [round(lo, 3), round(hi, 3)],
        "ci_excludes_zero": bool(lo > 0 or hi < 0) if lo == lo else False,
        "plausibility_weighted_delta": round(weighted_num / weighted_den, 3) if weighted_den else None,
        "sign": {"wins": wins, "losses": losses, "ties": ties},
        "classes": {k: sum(1 for v in classes.values() if v == k)
                    for k in ("ceiling", "floor", "discriminating", "weak", "inverted")},
        "inverted_cases": [cid for cid, c in classes.items() if c == "inverted"],
        "ceiling_cases": [cid for cid, c in classes.items() if c == "ceiling"],
        "per_case": {cid: {"base": b, "test": t, "delta": round(t - b, 3), "class": classes[cid]}
                     for cid, b, t in paired},
    }


def cost_per_pass(runs: list[dict]) -> dict[str, dict]:
    out = {}
    by_arm: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        by_arm[run["arm"]].append(run)
    for arm, rs in by_arm.items():
        passed = sum(1 for r in rs if r.get("passed"))
        tokens = [r.get("tokens", 0) for r in rs]
        durations = [r.get("duration_ms", 0) for r in rs]
        out[arm] = {
            "runs": len(rs),
            "passed": passed,
            # Median, not mean: latency and token tails are long and one slow
            # run should not decide the cost comparison.
            "median_tokens": int(statistics.median(tokens)) if tokens else 0,
            "median_duration_ms": int(statistics.median(durations)) if durations else 0,
            "total_cost_usd": round(sum(r.get("cost", 0) for r in rs), 2),
            # The only cost metric that trades quality against spend honestly.
            "tokens_per_passed_case": int(sum(tokens) / passed) if passed else None,
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs")
    parser.add_argument("--cases", help="cases.json, for plausibility weighting and tags")
    parser.add_argument("--base", default="A0")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--out")
    args = parser.parse_args()

    data = json.loads(Path(args.runs).read_text())
    runs = data["runs"]
    rates = per_case_rates(runs)

    cases: dict[str, dict] = {}
    if args.cases:
        for case in json.loads(Path(args.cases).read_text())["cases"]:
            cases[case["id"]] = case

    arms = sorted({r["arm"] for r in runs})
    contrasts = [c for arm in arms if arm != args.base
                 for c in [contrast(rates, cases, args.base, arm, args.bootstrap, args.seed)] if c]

    # Sub-suites and conformance cases are reported apart, never summed: one
    # measures correctness, the other agreement with the skill's author.
    subsets: dict[str, dict] = {}
    tagged = defaultdict(list)
    for cid, case in cases.items():
        if case.get("sub_suite"):
            tagged[f"sub_suite:{case['sub_suite']}"].append(cid)
        if case.get("conformance"):
            tagged["conformance"].append(cid)
        if case.get("off_map"):
            tagged["off_map"].append(cid)
    for label, ids in tagged.items():
        subset_rates = {cid: r for cid, r in rates.items() if cid in ids}
        for arm in arms:
            if arm == args.base:
                continue
            c = contrast(subset_rates, cases, args.base, arm, args.bootstrap, args.seed)
            if c:
                subsets.setdefault(label, {})[c["contrast"]] = {
                    k: c[k] for k in ("n_cases", "mean_base", "mean_test", "delta_all", "sign")
                }

    # Ceiling is a property of the eval SET: a case that every arm aces cannot
    # tell arms apart, whatever the skill does. So the test is min across arms,
    # not max and not the base arm. "Some arm aced it" would just mean solvable.
    total = len(rates)
    ceiling_n = sum(1 for r in rates.values() if r and min(r.values()) >= CEILING)
    audit = error_audit(runs)
    report = {
        "source": args.runs,
        "error_audit": audit,
        "skill_sha": data.get("skill_sha"),
        "model": data.get("model"),
        "arms": data.get("arms"),
        "eval_set_quality": {
            "n_cases": total,
            "n_ceiling": ceiling_n,
            "ceiling_fraction": round(ceiling_n / total, 3) if total else None,
            "note": ("Ceiling cases pass in both arms and measure the model, not the skill. "
                     "A suite that is mostly ceiling is not measuring what it claims to."),
        },
        "contrasts": contrasts,
        "subsets": subsets,
        "cost": cost_per_pass(runs),
        "power_note": (f"With {total} cases this design detects roughly >=0.17 reliably and cannot "
                       "distinguish +0.05 from zero. Treat the base-vs-full contrast as the single "
                       "confirmatory test; every other contrast is exploratory."),
    }

    if not audit["trustworthy"]:
        print(f"!! ERROR RATE {audit['overall_rate']:.0%} overall, spread {audit['spread_across_arms']:.0%} "
              f"across arms -- results NOT trustworthy: {audit['per_arm']}")
        print()
    print(f"{'contrast':16} {'n':>3} {'base':>6} {'test':>6} {'delta':>7} {'ci95':>16}  sign")
    for c in contrasts:
        sign = f"+{c['sign']['wins']}/-{c['sign']['losses']}/={c['sign']['ties']}"
        print(f"{c['contrast']:16} {c['n_cases']:>3} {c['mean_base']:>6.2f} {c['mean_test']:>6.2f} "
              f"{c['delta_all']:>+7.3f} [{c['ci95'][0]:>+.2f},{c['ci95'][1]:>+.2f}]  {sign}")
        if c["inverted_cases"]:
            print(f"    INVERTED (skill worse than baseline): {', '.join(c['inverted_cases'])}")
        if c["ceiling_cases"]:
            print(f"    ceiling (excluded from headline): {', '.join(c['ceiling_cases'])}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
        print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
