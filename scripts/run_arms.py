#!/usr/bin/env python3
"""Run an eval suite across ablation arms and score it mechanically.

The arms exist because "with skill vs without skill" answers whether the skill
helps but cannot answer whether it is NEEDED. A skill that beats nothing has
only shown that a nudge in the right direction helps; the interesting question
is whether 1,900 lines beat five.

  A0 none          floor - what the base model does unaided
  A1 hint          the skill compressed to ~5 lines of system prompt
  A2 skill_md      SKILL.md body only, references withheld
  A3 full          the skill as designed, progressive disclosure intact
  A4 full_forced   SKILL.md + every reference concatenated into the prompt

Contrasts and what each one settles:

  A3 - A0   does it help at all
  A3 - A1   does the content beat a five-line nudge      <- the necessity test
  A3 - A2   do the reference files earn their tokens
  A4 - A3   are the references useful but never opened   <- a discovery failure,
            which is the same defect as a dangling pointer, only milder

Scoring is mechanical: an enum equality on the forced JSON output plus a
forbidden-substring check. No model grades another model's answer, so there is
no self-grading bias and no grader variance to argue about.

Arms are interleaved rather than run in blocks, so that any drift over a long
run spreads across all arms instead of landing on whichever ran last.

Usage:
    python scripts/run_arms.py evals/diagnose/cases.json \
        --schema evals/diagnose/schema.json \
        --skill-dir . --arms A0:3,A3:3 --out evals/results/pilot
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

A3_POINTER = (
    "A reference skill is available at {skill}/SKILL.md. Read it before answering, "
    "along with any files under {skill}/references/ that it points to and that are "
    "relevant to this problem."
)

_lock = threading.Lock()


def log(msg: str) -> None:
    with _lock:
        print(msg, file=sys.stderr, flush=True)


def concat_skill(skill_dir: Path) -> str:
    parts = [(skill_dir / "SKILL.md").read_text(encoding="utf-8")]
    refs = skill_dir / "references"
    if refs.is_dir():
        for ref in sorted(refs.glob("*.md")):
            parts.append(f"\n\n===== {ref.name} =====\n\n" + ref.read_text(encoding="utf-8"))
    return "".join(parts)


def skill_md_body(skill_dir: Path) -> str:
    """SKILL.md with its frontmatter stripped - the frontmatter is triggering
    metadata, not instruction, and including it would test the wrong thing."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip()
    return text


def build_arm_cmd(arm: str, prompt: str, schema: str, ctx: dict) -> list[str]:
    cmd = ["claude", "-p", prompt, "--safe-mode", "--model", ctx["model"],
           "--output-format", "json", "--json-schema", schema,
           "--max-budget-usd", str(ctx["budget"])]

    if arm == "A0":
        cmd += ["--tools", ""]
    elif arm == "A1":
        cmd += ["--tools", "", "--append-system-prompt", ctx["hint"]]
    elif arm == "A2":
        cmd += ["--tools", "", "--append-system-prompt", ctx["skill_md"]]
    elif arm == "A3":
        # --tools is variadic, so these are three tool names, not one name plus
        # two stray positionals. Verified with a planted file: in this arm the
        # model uses Glob to find it and Grep to search it. The asymmetry with
        # the other arms' `--tools ""` reads like a bug and is not one.
        cmd += ["--tools", "Read", "Glob", "Grep",
                "--add-dir", ctx["skill_copy"],
                "--append-system-prompt", A3_POINTER.format(skill=ctx["skill_copy"])]
    elif arm == "A4":
        cmd += ["--tools", "", "--append-system-prompt", ctx["skill_full"]]
    else:
        raise ValueError(f"unknown arm {arm}")
    return cmd


def normalise_tool(name: str, synonyms: dict[str, list[str]]) -> str | None:
    """Map a free-text tool name onto a canonical key.

    'JUnit 6 (Jupiter)', 'JUnit 6' and 'Jupiter 6' are the same answer, and a
    scorer that treats them as different measures phrasing rather than routing.
    """
    lowered = (name or "").strip().lower()
    if not lowered:
        return None
    best: tuple[int, str] | None = None
    for canonical, variants in synonyms.items():
        for variant in variants:
            if variant in lowered:
                # Longest match wins, so "junit 6" is not swallowed by "junit".
                if best is None or len(variant) > best[0]:
                    best = (len(variant), canonical)
    return best[1] if best else lowered


def score_route(case: dict, output: dict | None, cfg: dict) -> dict:
    """Score the jvm-testing routing suite.

    Assertions differ by sub-suite because the sub-suites measure different
    things - routing correctness, editorial conformance, and the two behaviours
    SKILL.md claims about itself.
    """
    if output is None:
        return {"passed": False, "answered": False, "predicted": None}

    synonyms = cfg.get("synonyms", {})
    cut_tools = [t.lower() for t in cfg.get("cut_tools", [])]

    predicted_raw = output.get("tool", "")
    predicted = normalise_tool(predicted_raw, synonyms)
    checks: dict[str, bool] = {}

    if "expect_off_map" in case:
        checks["off_map_correct"] = bool(output.get("off_map")) == case["expect_off_map"]
    if case.get("expect_verify_version"):
        checks["flagged_currency"] = bool(output.get("would_verify_version"))
    if case.get("key"):
        # A key may name several acceptable answers. On the Kotest case the point
        # is "do not adopt a second-engine spec framework", not which JUnit major,
        # so both junit5 and junit6 are right and pinning one measures phrasing.
        accepted = case["key"] if isinstance(case["key"], list) else [case["key"]]
        checks["correct_tool"] = predicted in accepted

    if case.get("sub_suite") == "negative":
        # Match the tool actually RECOMMENDED, not any substring of the answer.
        # "JUnit Jupiter, optionally with kotest-assertions-core" recommends
        # Jupiter; the assertions module needs no second Platform engine, so it
        # does not violate the one-engine rule the cut list exists to protect.
        checks["avoided_cut_tool"] = predicted not in cut_tools

    return {
        "passed": all(checks.values()) if checks else False,
        "answered": True,
        "predicted": predicted,
        "predicted_raw": predicted_raw,
        "off_map": output.get("off_map"),
        "would_verify_version": output.get("would_verify_version"),
        "checks": checks,
    }


def score(case: dict, output: dict | None, raw: str) -> dict:
    """Mechanical scoring. Two assertions, both exact equality on forced enums.

    correct_class     the diagnosis enum equals the key
    correct_proposal  where the user proposed or already applied a fix, the
                      verdict on that proposal is right

    The second assertion replaced a forbidden-substring check that did not
    survive its first smoke test: both arms correctly answered "do NOT move to
    ZGC" and both were scored as failures, because the refutation contains the
    word ZGC. Substring matching cannot tell endorsement from rejection, so the
    model is made to commit to an enum instead. must_not_say survives only as a
    reported flag - it never decides pass or fail.
    """
    if output is None:
        return {"correct_class": False, "correct_proposal": False, "passed": False,
                "answered": False, "predicted": None}

    predicted = output.get("root_cause_class") or output.get("tool")
    correct = predicted == case.get("key")

    proposal_key = case.get("proposal_key")
    predicted_proposal = output.get("user_proposal_verdict")
    if proposal_key:
        # partially_endorse against a "reject" key is a miss: half-endorsing a
        # plan the evidence contradicts still sends the user to file the ticket.
        correct_proposal = predicted_proposal == proposal_key
    else:
        correct_proposal = True

    haystack = json.dumps(output).lower()
    flags = [s for s in case.get("must_not_say", []) if s.lower() in haystack]

    return {
        "correct_class": correct,
        "correct_proposal": correct_proposal,
        "predicted_proposal": predicted_proposal,
        "mention_flags": flags,
        "passed": correct and correct_proposal,
        "answered": True,
        "predicted": predicted,
    }


def _score_none(case: dict, ctx: dict) -> dict:
    if ctx.get("suite_cfg", {}).get("synonyms"):
        return score_route(case, None, ctx["suite_cfg"])
    return score(case, None, "")


def run_one(job: dict, ctx: dict) -> dict:
    case, arm, rep = job["case"], job["arm"], job["rep"]
    prompt = case["prompt"]
    if case.get("artifact"):
        prompt += "\n\n" + case["artifact"]

    cmd = build_arm_cmd(arm, prompt, ctx["schema"], ctx)
    result = {"case_id": case["id"], "case_name": case.get("name", case["id"]),
              "arm": arm, "rep": rep, "sub_suite": case.get("sub_suite"),
              "key": case.get("key"), "cost": 0.0, "duration_ms": 0, "tokens": 0}

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=ctx["timeout"])
    except subprocess.TimeoutExpired:
        result.update(_score_none(case, ctx), error="timeout")
        return result

    if proc.returncode != 0:
        result.update(_score_none(case, ctx), error=f"exit {proc.returncode}: {proc.stderr[-200:]}")
        return result

    try:
        env = json.loads(proc.stdout)
    except json.JSONDecodeError:
        result.update(_score_none(case, ctx), error="unparseable envelope")
        return result

    usage = env.get("usage") or {}
    result["cost"] = float(env.get("total_cost_usd") or 0.0)
    result["duration_ms"] = env.get("duration_ms") or 0
    result["tokens"] = (usage.get("output_tokens") or 0) + (usage.get("input_tokens") or 0) \
        + (usage.get("cache_creation_input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)

    output = env.get("structured_output")
    result["output"] = output
    if ctx.get("suite_cfg", {}).get("synonyms"):
        result.update(score_route(case, output, ctx["suite_cfg"]))
    else:
        result.update(score(case, output, proc.stdout))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases")
    parser.add_argument("--schema", required=True)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--hint", help="file with the A1 five-line compression")
    parser.add_argument("--arms", default="A0:3,A3:3", help="e.g. A0:5,A1:3,A2:3,A3:5,A4:3")
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--budget", type=float, default=1.50)
    parser.add_argument("--only", help="comma-separated case ids, for smoke tests")
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    data = json.loads(Path(args.cases).read_text())
    cases = data["cases"]
    if args.only:
        wanted = {c.strip() for c in args.only.split(",")}
        cases = [c for c in cases if c["id"] in wanted]

    plan = []
    for spec in args.arms.split(","):
        arm, _, reps = spec.partition(":")
        plan.append((arm.strip(), int(reps or 3)))

    # Copy the skill somewhere stable for A3 to read. Never point A3 at an
    # installed copy: the whole reason this evaluation exists is that the
    # installed one had drifted from the repo.
    tmpdir = tempfile.mkdtemp(prefix="skillcopy-")
    skill_copy = Path(tmpdir) / skill_dir.name
    shutil.copytree(skill_dir, skill_copy,
                    ignore=shutil.ignore_patterns(".git", "evals", "scripts", "dist"))

    sha = subprocess.run(["git", "-C", str(skill_dir), "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()

    ctx = {
        "model": args.model,
        "timeout": args.timeout,
        "budget": args.budget,
        "schema": Path(args.schema).read_text(),
        "skill_copy": str(skill_copy),
        "skill_md": skill_md_body(skill_dir),
        "skill_full": concat_skill(skill_dir),
        "hint": Path(args.hint).read_text() if args.hint else "",
        "suite_cfg": data,
    }

    jobs = [{"case": c, "arm": arm, "rep": r}
            for c in cases for arm, reps in plan for r in range(reps)]
    random.Random(args.seed).shuffle(jobs)  # interleave arms against drift

    log(f"{len(cases)} cases x {plan} = {len(jobs)} runs, {args.workers} workers")

    results, done = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, j, ctx): j for j in jobs}
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            if done % 10 == 0 or done == len(jobs):
                spent = sum(r["cost"] for r in results)
                log(f"  {done}/{len(jobs)}  ${spent:.2f}")

    shutil.rmtree(tmpdir, ignore_errors=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "runs.json").write_text(json.dumps({
        "suite": data.get("suite"),
        "skill_dir": str(skill_dir),
        "skill_sha": sha,
        "model": args.model,
        "arms": dict(plan),
        "total_cost_usd": round(sum(r["cost"] for r in results), 2),
        "runs": results,
    }, indent=2) + "\n")

    log(f"\n{len(results)} runs, ${sum(r['cost'] for r in results):.2f} -> {out / 'runs.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
