#!/usr/bin/env python3
"""Extract checkable claims from a skill's markdown, for the redundancy audit.

A skill only earns its tokens where it tells the model something the model does
not already reliably produce. To find that, first decompose the skill into
claims that can be checked one at a time.

Each claim gets two probes, because they measure different things:

  probe_asked   — a direct question. Does the model KNOW this?
  probe_task    — a realistic scenario that does not name the fact. Does the
                  model REACH FOR it unprompted?

The gap between the two is the elicitation gap, and it is the whole business of
a checklist-style skill: content the model knows but does not deploy is worth
keeping as a short reminder, not as prose. Measuring only the direct question
would tell you to delete exactly that content.

`probe_asked` must not contain its own answer. That is the single most common
way this audit goes wrong — a leaked probe inflates the "model already knows
it" rate and argues for cutting good content — so every probe is re-read by
`audit_probes.py` before any of them are run.

Usage:
    python scripts/extract_claims.py SKILL_DIR --out evals/redundancy/claims.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "section": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["numeric", "procedural", "tool_choice", "antipattern", "curation"],
                    },
                    "probe_asked": {"type": "string"},
                    "probe_task": {"type": "string"},
                    "answer_key": {"type": "string"},
                },
                "required": ["claim", "section", "type", "probe_asked", "probe_task", "answer_key"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["claims"],
    "additionalProperties": False,
}

PROMPT = """Read the file at {path}.

Extract exactly {n} of its most CHECKABLE, FALSIFIABLE claims — a version fact, a
numeric threshold, a "reach for X not Y" routing decision, or a named anti-pattern.
Skip framing, motivation, and anything whose correctness is a matter of taste.

Prefer claims that a competent engineer could get wrong, and spread them across the
file's sections rather than clustering in one.

For each claim produce:

- claim: the assertion, one sentence.
- section: the nearest '##' heading it came from.
- type: one of numeric | procedural | tool_choice | antipattern | curation.
  Use "curation" ONLY for claims that are this author's private editorial choice
  (e.g. "we deliberately do not recommend tool X"). Nobody can know those from
  general knowledge, so they are scored separately.
- probe_asked: a direct question testing whether someone knows this.
  CRITICAL: the question must NOT contain or paraphrase its own answer. Ask "what
  is the threshold for X?", never "is the threshold for X greater than 10ms?".
  A question that leaks its answer silently corrupts the whole measurement.
- probe_task: a realistic engineer's scenario, 1-3 sentences, where acting well
  REQUIRES this claim but where the claim, its key terms, and its answer are all
  ABSENT from the wording. Describe a situation, do not ask about the fact.
- answer_key: what a correct response must contain, terse.

Return only the structured object."""


def extract(md_path: Path, skill_dir: Path, n: int, model: str) -> list[dict]:
    cmd = [
        "claude", "-p", PROMPT.format(path=md_path, n=n),
        "--safe-mode",
        "--tools", "Read",
        "--add-dir", str(skill_dir),
        "--model", model,
        "--output-format", "json",
        "--json-schema", json.dumps(SCHEMA),
    ]
    env_note = md_path.relative_to(skill_dir)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT {env_note}", file=sys.stderr)
        return []

    if proc.returncode != 0:
        print(f"  FAILED  {env_note}: {proc.stderr[-300:]}", file=sys.stderr)
        return []

    try:
        envelope = json.loads(proc.stdout)
        payload = envelope.get("structured_output") or json.loads(envelope["result"])
        claims = payload["claims"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"  UNPARSEABLE {env_note}: {exc}", file=sys.stderr)
        return []

    for claim in claims:
        claim["file"] = str(env_note)
    print(f"  {len(claims):2d} claims  {env_note}", file=sys.stderr)
    return claims


def allocate(md_files: list[Path], target: int, floor: int, ceiling: int) -> dict[Path, int]:
    """Spread the claim budget by file length, so every file gets a verdict.

    A flat split would starve a 340-line file and over-sample a 97-line one; a
    pure proportional split would give the shortest file so few claims that its
    section rate means nothing. Hence the floor and ceiling.
    """
    lengths = {f: len(f.read_text(encoding="utf-8").splitlines()) for f in md_files}
    total = sum(lengths.values()) or 1
    return {
        f: max(floor, min(ceiling, round(target * length / total)))
        for f, length in lengths.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir")
    parser.add_argument("--out", required=True)
    parser.add_argument("--target", type=int, default=40, help="total claims across all files")
    parser.add_argument("--floor", type=int, default=3, help="minimum claims per file")
    parser.add_argument("--ceiling", type=int, default=8, help="maximum claims per file")
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    md_files = [skill_dir / "SKILL.md"]
    refs = skill_dir / "references"
    if refs.is_dir():
        md_files.extend(sorted(refs.glob("*.md")))

    budget = allocate(md_files, args.target, args.floor, args.ceiling)
    print(f"Extracting from {len(md_files)} files (target {args.target}):", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = pool.map(lambda f: extract(f, skill_dir, budget[f], args.model), md_files)

    claims: list[dict] = []
    for batch in results:
        for claim in batch:
            claim["id"] = f"C{len(claims):03d}"
            claims.append(claim)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"skill_dir": str(skill_dir), "claims": claims}, indent=2) + "\n")

    by_type: dict[str, int] = {}
    for claim in claims:
        by_type[claim["type"]] = by_type.get(claim["type"], 0) + 1
    print(f"\n{len(claims)} claims -> {out}", file=sys.stderr)
    print(f"  by type: {by_type}", file=sys.stderr)
    return 0 if claims else 1


if __name__ == "__main__":
    sys.exit(main())
