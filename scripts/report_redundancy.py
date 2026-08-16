#!/usr/bin/env python3
"""Turn redundancy probe results into a per-file, per-section keep/cut verdict.

Reads the output of probe_redundancy.py and rolls the per-claim rates up to the
unit you actually make decisions about: the reference file, and the section
within it.

Two reporting rules matter here:

1. "curation" claims are reported separately and never folded into the headline.
   A private editorial decision ("we deliberately do not recommend Turbine") is
   unknowable from general knowledge, so it scores ~0 redundancy by construction.
   Averaging it in would make every curated skill look indispensable.

2. The verdict is advisory, not final. A section the model already knows can
   still earn its place if its framing changes behaviour in the task evals —
   that is what the ablation arms are for. This report decides where to SPEND
   the expensive measurement, and breaks ties at the end.

Usage:
    python scripts/report_redundancy.py evals/redundancy/results.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

VERDICT_NOTE = {
    "CUT": "model knows it and uses it unprompted",
    "COMPRESS": "model knows it but does not reach for it - keep the reminder, drop the prose",
    "TRIM": "model is unreliable here - keep the specific claims, cut the surrounding prose",
    "KEEP": "genuine payload - the model does not have this",
}


def summarise(claims: list[dict]) -> dict:
    if not claims:
        return {"n": 0}
    n = len(claims)
    r_asked = sum(c["r_asked"] for c in claims) / n
    r_task = sum(c["r_task"] for c in claims) / n
    return {
        "n": n,
        "r_asked": round(r_asked, 3),
        "r_task": round(r_task, 3),
        "gap": round(r_asked - r_task, 3),
        "verdict": _verdict(r_asked, r_task),
    }


def _verdict(r_asked: float, r_task: float) -> str:
    if r_asked >= 0.8 and r_task >= 0.6:
        return "CUT"
    if r_asked >= 0.8:
        return "COMPRESS"
    if r_asked < 0.5:
        return "KEEP"
    return "TRIM"


def bar(value: float, width: int = 10) -> str:
    filled = round(value * width)
    return "#" * filled + "." * (width - filled)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results")
    parser.add_argument("--markdown", help="also write a markdown report here")
    args = parser.parse_args()

    data = json.loads(Path(args.results).read_text())
    all_claims = data["claims"]
    knowledge = [c for c in all_claims if c["type"] != "curation"]
    curation = [c for c in all_claims if c["type"] == "curation"]

    lines: list[str] = []

    def emit(text: str = "") -> None:
        lines.append(text)

    emit(f"# Redundancy audit — {Path(data['skill_dir']).name}")
    emit()
    emit(f"Subject `{data['subject_model']}` with no skill loaded, "
         f"{data['runs_per_probe']} runs per probe, {len(all_claims)} claims, "
         f"${data.get('total_cost_usd', 0):.2f}.")
    emit()
    emit("`R_asked` = knows the fact when asked directly. "
         "`R_task` = reaches for it unprompted in a realistic scenario. "
         "The gap between them is what a checklist buys.")
    emit()

    overall = summarise(knowledge)
    emit(f"**Overall (knowledge claims, n={overall['n']}): "
         f"R_asked {overall['r_asked']:.2f}, R_task {overall['r_task']:.2f}, "
         f"gap {overall['gap']:+.2f} -> {overall['verdict']}**")
    emit()

    emit("## By file")
    emit()
    emit("| File | n | R_asked | R_task | Gap | Verdict |")
    emit("|---|---|---|---|---|---|")
    by_file: dict[str, list[dict]] = defaultdict(list)
    for claim in knowledge:
        by_file[claim["file"]].append(claim)
    for path in sorted(by_file, key=lambda p: summarise(by_file[p])["r_asked"]):
        s = summarise(by_file[path])
        emit(f"| `{path}` | {s['n']} | {bar(s['r_asked'])} {s['r_asked']:.2f} "
             f"| {bar(s['r_task'])} {s['r_task']:.2f} | {s['gap']:+.2f} | **{s['verdict']}** |")
    emit()

    emit("## By section")
    emit()
    emit("| File | Section | n | R_asked | R_task | Verdict |")
    emit("|---|---|---|---|---|---|")
    by_section: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for claim in knowledge:
        by_section[(claim["file"], claim["section"])].append(claim)
    for (path, section) in sorted(by_section, key=lambda k: summarise(by_section[k])["r_asked"]):
        s = summarise(by_section[(path, section)])
        emit(f"| `{path}` | {section} | {s['n']} | {s['r_asked']:.2f} | {s['r_task']:.2f} "
             f"| **{s['verdict']}** |")
    emit()

    emit("## Highest-value claims (model least likely to know)")
    emit()
    emit("These are the skill's real payload. Task-eval assertions should be drawn from here —")
    emit("an assertion the base model already satisfies measures nothing.")
    emit()
    for claim in sorted(knowledge, key=lambda c: (c["r_asked"], c["r_task"]))[:10]:
        emit(f"- **{claim['r_asked']:.2f}/{claim['r_task']:.2f}** "
             f"`{claim['file']}` — {claim['claim']}")
    emit()

    emit("## Widest elicitation gaps (knows it, does not use it)")
    emit()
    emit("Content to compress into a checklist rather than delete: the model has the fact")
    emit("but will not produce it unless prompted.")
    emit()
    for claim in sorted(knowledge, key=lambda c: -c["elicitation_gap"])[:8]:
        if claim["elicitation_gap"] <= 0:
            break
        emit(f"- **gap {claim['elicitation_gap']:+.2f}** ({claim['r_asked']:.2f} -> {claim['r_task']:.2f}) "
             f"`{claim['file']}` — {claim['claim']}")
    emit()

    emit("## Dead weight (model knows it and already uses it)")
    emit()
    dead = [c for c in knowledge if c["verdict"] == "CUT"]
    if dead:
        for claim in sorted(dead, key=lambda c: -c["r_task"])[:10]:
            emit(f"- **{claim['r_asked']:.2f}/{claim['r_task']:.2f}** "
                 f"`{claim['file']}` — {claim['claim']}")
    else:
        emit("_None — no claim was both known and spontaneously used._")
    emit()

    if curation:
        s = summarise(curation)
        emit("## Curation claims (reported separately, never averaged in)")
        emit()
        emit(f"{s['n']} claims, R_asked {s['r_asked']:.2f}. These encode this author's editorial")
        emit("choices, which nobody can know from general knowledge. A low score here is")
        emit("arithmetic, not evidence of value: it says the decision is private, not that")
        emit("following it produces better outcomes. Only the task evals can show that.")
        emit()

    emit("## What the verdicts mean")
    emit()
    for verdict, note in VERDICT_NOTE.items():
        emit(f"- **{verdict}** — {note}")
    emit()
    emit("This audit decides where to spend the expensive task evals, and breaks ties at")
    emit("the end. It does not on its own justify deleting a section: framing can change")
    emit("behaviour in ways a decomposition into claims does not capture.")

    report = "\n".join(lines)
    print(report)
    if args.markdown:
        out = Path(args.markdown)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report + "\n")
    return 0


if __name__ == "__main__":
    main()
