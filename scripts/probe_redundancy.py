#!/usr/bin/env python3
"""Measure how much of a skill the base model already knows.

For every claim, two rates are measured against a model with NO skill loaded:

  R_asked  — asked directly, does it know the fact?
  R_task   — given a realistic scenario that never names the fact, does it
             actually reach for it?

Reporting only R_asked is the trap. A model can know that HikariCP acquire
time above 10ms is alarming and still never think to look at acquire time when
someone says "the app is slow" — and closing that gap is precisely what a
checklist-shaped skill is for. So the two rates drive different verdicts:

  R_asked high, R_task high  -> cut; the model knows it and uses it
  R_asked high, R_task low   -> compress to a one-line reminder; the content is
                                redundant but the prompt to look is not
  R_asked low                -> keep verbatim; this is the skill's real payload

Subject runs use --safe-mode --tools "" so nothing but the model's own weights
answers — a web lookup would measure the internet, not the model.

Grading is a separate call that sees only {claim, answer_key, response}: never
the skill text (halo effect) and never which probe produced the response.

Usage:
    python scripts/probe_redundancy.py evals/redundancy/claims.json \
        --out evals/redundancy/results.json --runs 3
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Without this, the model frequently emits a fabricated "Tool Use: Read" block
# and stops, producing no answer at all. Those runs are not evidence that it
# lacks the knowledge - they are a prompt-format failure - but a naive grader
# scores them "absent" and the skill looks more necessary than it is.
SUBJECT_SUFFIX = (
    "\n\nYou have no tools available in this session. Do not attempt to read files, "
    "search, or call any tool, and do not write out tool-call blocks. Answer directly "
    "from your own knowledge.\n\nAnswer concisely — a few sentences at most."
)

# A run that returns nothing measured nothing. Retry it; if it still comes back
# empty, mark it invalid and drop it from the denominator. Scoring an
# infrastructure failure as "the model does not know this" biases every rate
# downward, which is the direction that flatters the skill.
MAX_ATTEMPTS = 3
MIN_ANSWER_CHARS = 40

GRADER_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "verdict": {"type": "string", "enum": ["knows", "partial", "wrong", "absent"]},
                    "evidence": {"type": "string"},
                },
                "required": ["index", "verdict", "evidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}

GRADER_PROMPT = """You are grading whether each response below demonstrates a specific piece of knowledge.

THE KNOWLEDGE BEING TESTED:
{claim}

WHAT A CORRECT RESPONSE MUST CONTAIN:
{answer_key}

Grade each response independently:
- "knows"   — states the key content correctly, in its own words is fine
- "partial" — gestures at it, or gets it half right, or right but badly hedged
- "wrong"   — makes a claim that contradicts the key
- "absent"  — never addresses it at all

Judge only against the key above. Do not reward a response for being generally
sensible, well written, or thorough — a long, competent answer that never lands
the specific point is "absent", not "partial". Do not penalise brevity.

RESPONSES:
{responses}

Return one verdict per response, using its index."""

_print_lock = threading.Lock()


def log(message: str) -> None:
    with _print_lock:
        print(message, file=sys.stderr, flush=True)


def run_claude(prompt: str, model: str, schema: dict | None, timeout: int,
               budget: float, cwd: str | None = None) -> tuple[str | dict | None, float]:
    cmd = [
        "claude", "-p", prompt,
        "--safe-mode",
        # Verified against a planted-token test: --tools "" is what actually
        # withholds tools. --disallowed-tools does not (the model still reaches
        # the file by another route), and no flag at all obviously does not.
        "--tools", "",
        "--model", model,
        "--output-format", "json",
        "--max-budget-usd", str(budget),
    ]
    if schema is not None:
        cmd.extend(["--json-schema", json.dumps(schema)])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        return None, 0.0
    if proc.returncode != 0:
        return None, 0.0

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, 0.0

    cost = float(envelope.get("total_cost_usd") or 0.0)
    if envelope.get("is_error"):
        return None, cost
    if schema is not None:
        return envelope.get("structured_output"), cost
    return envelope.get("result"), cost


def looks_answered(text: str | None) -> bool:
    """Reject non-answers so they can be retried rather than silently scored 0."""
    if not text or len(text.strip()) < MIN_ANSWER_CHARS:
        return False
    stripped = text.strip()
    # A fabricated tool-call block with nothing after it is not an answer.
    if stripped.startswith("**Tool Use") and "Tool Result" not in stripped:
        return False
    return True


def probe_claim(claim: dict, runs: int, model: str, timeout: int, budget: float, cwd: str) -> dict:
    """Run both probes N times each. Returns raw responses; grading is separate."""
    record = {"id": claim["id"], "responses": {"asked": [], "task": []},
              "cost": 0.0, "invalid": {"asked": 0, "task": 0}}
    for kind, key in (("asked", "probe_asked"), ("task", "probe_task")):
        for _ in range(runs):
            text = None
            for _attempt in range(MAX_ATTEMPTS):
                text, cost = run_claude(claim[key] + SUBJECT_SUFFIX, model, None, timeout, budget, cwd)
                record["cost"] += cost
                if looks_answered(text):
                    break
            if looks_answered(text):
                record["responses"][kind].append(text)
            else:
                record["invalid"][kind] += 1
    return record


def grade_claim(claim: dict, record: dict, model: str, timeout: int, budget: float) -> dict:
    """Grade all of a claim's responses in one call, so the grader is cheap.

    The grader never learns which responses came from which probe, so it cannot
    grade the task probe more leniently just because it knows the fact was not
    mentioned in the question.
    """
    flat = record["responses"]["asked"] + record["responses"]["task"]
    blocks = "\n\n".join(
        f"--- RESPONSE {i} ---\n{(text or '(empty)')[:4000]}" for i, text in enumerate(flat)
    )
    prompt = GRADER_PROMPT.format(
        claim=claim["claim"], answer_key=claim["answer_key"], responses=blocks)

    # Retry, because grader calls fail transiently under concurrency. An earlier
    # run lost 79% of its verdicts this way and the losses were scored as
    # "absent" - i.e. as the model not knowing the material - which is the
    # direction that makes the skill look necessary. A grader failure is missing
    # data, never evidence.
    scores: dict[int, dict] = {}
    for _attempt in range(MAX_ATTEMPTS):
        payload, cost = run_claude(prompt, model, GRADER_SCHEMA, timeout, budget)
        record["cost"] += cost
        if payload:
            for verdict in payload.get("verdicts", []):
                if isinstance(verdict.get("index"), int):
                    scores[verdict["index"]] = verdict
        if len(scores) == len(flat):
            break

    # Anything still missing is marked ungraded and dropped from the rate rather
    # than counted as a miss.
    n = len(record["responses"]["asked"])
    ungraded = {"verdict": "ungraded", "evidence": "grader returned no verdict for this response"}
    record["verdicts"] = {
        "asked": [scores.get(i, dict(ungraded)) for i in range(n)],
        "task": [scores.get(i, dict(ungraded)) for i in range(n, len(flat))],
    }
    record["ungraded"] = len(flat) - len(scores)
    return record


# A "partial" is genuinely half a hit: the model has the idea but not reliably
# enough to depend on. Counting it as a miss would overstate the skill's value;
# counting it as a hit would understate it.
POINTS = {"knows": 1.0, "partial": 0.5, "wrong": 0.0, "absent": 0.0}


def rate(verdicts: list[dict]) -> float | None:
    """None, not 0.0, when there is nothing to score. A claim with no gradeable
    responses has no measurement; reporting it as 0% known would be a fabricated
    data point that happens to favour keeping the skill."""
    scored = [v for v in verdicts if v["verdict"] in POINTS]
    if not scored:
        return None
    return sum(POINTS[v["verdict"]] for v in scored) / len(scored)


def verdict_for(r_asked: float, r_task: float) -> str:
    if r_asked >= 0.8 and r_task >= 0.6:
        return "CUT"
    if r_asked >= 0.8:
        return "COMPRESS"
    if r_asked < 0.5:
        return "KEEP"
    return "TRIM"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims")
    parser.add_argument("--out", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--model", default="claude-opus-5", help="subject: the model users actually run")
    parser.add_argument("--grader-model", default="claude-sonnet-5",
                        help="grading against an explicit key is easy; no need to pay for the big model")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--budget", type=float, default=0.75, help="per-call ceiling, USD")
    parser.add_argument("--no-resume", action="store_true",
                        help="ignore an existing checkpoint and re-probe everything")
    args = parser.parse_args()

    data = json.loads(Path(args.claims).read_text())
    claims = data["claims"]
    log(f"Probing {len(claims)} claims x {args.runs} runs x 2 probes = {len(claims) * args.runs * 2} calls")

    # Run subjects from an empty directory. Belt and braces on top of --tools "":
    # if isolation ever regresses, there is nothing here to find.
    sandbox = tempfile.mkdtemp(prefix="probe-sandbox-")

    # Checkpoint every claim as it lands. This run costs real money and takes
    # tens of minutes; without this, any interruption throws away everything and
    # the audit never finishes in an environment that restarts.
    checkpoint = Path(args.out).with_suffix(".checkpoint.jsonl")
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}
    if checkpoint.exists() and not args.no_resume:
        for line in checkpoint.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                records[rec["id"]] = rec
        log(f"resuming: {len(records)} claims already probed")

    todo = [c for c in claims if c["id"] not in records]
    done = len(records)
    write_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(probe_claim, c, args.runs, args.model, args.timeout, args.budget, sandbox): c
            for c in todo
        }
        for future in as_completed(futures):
            claim = futures[future]
            record = future.result()
            records[claim["id"]] = record
            with write_lock, checkpoint.open("a") as fh:
                fh.write(json.dumps(record) + "\n")
            done += 1
            if done % 5 == 0 or done == len(claims):
                log(f"  probed {done}/{len(claims)}")

    def needs_grading(rec: dict) -> bool:
        if "verdicts" not in rec:
            return True
        return any(v["verdict"] in ("ungraded",) or v.get("evidence") == "ungraded"
                   for k in ("asked", "task") for v in rec["verdicts"][k])

    ungraded = [c for c in claims if needs_grading(records[c["id"]])]
    log(f"Grading {len(ungraded)} claims ({len(claims) - len(ungraded)} already graded)...")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(grade_claim, c, records[c["id"]], args.grader_model, args.timeout, args.budget): c
            for c in ungraded
        }
        for future in as_completed(futures):
            future.result()
    # Rewrite the checkpoint with verdicts folded in, so a restart after this
    # point does not re-pay for grading either.
    with checkpoint.open("w") as fh:
        for rec in records.values():
            fh.write(json.dumps(rec) + "\n")

    results = []
    dropped = 0
    for claim in claims:
        record = records[claim["id"]]
        r_asked = rate(record["verdicts"]["asked"])
        r_task = rate(record["verdicts"]["task"])
        if r_asked is None or r_task is None:
            dropped += 1
            continue
        results.append({
            **{k: claim[k] for k in ("id", "file", "section", "type", "claim", "answer_key")},
            "r_asked": r_asked,
            "r_task": r_task,
            "elicitation_gap": round(r_asked - r_task, 3),
            "n_asked": len(record["verdicts"]["asked"]),
            "n_task": len(record["verdicts"]["task"]),
            "invalid_runs": record["invalid"]["asked"] + record["invalid"]["task"],
            "verdict": verdict_for(r_asked, r_task),
            "verdicts": record["verdicts"],
        })

    total_cost = sum(r["cost"] for r in records.values())
    total_invalid = sum(r["invalid"]["asked"] + r["invalid"]["task"] for r in records.values())
    attempted = len(claims) * args.runs * 2
    log(f"invalid runs excluded: {total_invalid}/{attempted} ({total_invalid/attempted:.0%}); "
        f"claims dropped for having no valid data: {dropped}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "skill_dir": data.get("skill_dir"),
        "subject_model": args.model,
        "grader_model": args.grader_model,
        "runs_per_probe": args.runs,
        "total_cost_usd": round(total_cost, 2),
        "invalid_runs_excluded": total_invalid,
        "ungraded_responses": sum(r.get("ungraded", 0) for r in records.values()),
        "claims_dropped_no_data": dropped,
        "claims": results,
    }, indent=2) + "\n")

    log(f"\n{len(results)} claims graded, ${total_cost:.2f} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
