#!/usr/bin/env python3
"""Measure whether a skill actually gets invoked for a query.

Why this exists rather than skill-creator's run_eval.py: that harness registers
the skill's *description* as a temporary slash command and checks whether Claude
reaches for that synthetic command. Two problems. It measures a proxy rather
than real skill discovery, and when a skill of the same name is genuinely
installed the model invokes the real one — so the detector looks for its
synthetic name, fails to find it, and records a non-trigger. Run against both
skills here it returned a uniform 0.00 on positives AND negatives, which is the
signature of a broken detector rather than a bad description: a genuinely poor
description produces variance, not silence.

This instead installs the real skill into a scratch project, runs the query
there, and watches the tool stream for the skill actually being invoked — either
via the Skill tool or by reading its SKILL.md.

Detection is deliberately generous about *when*: the model may run other tools
before deciding to consult the skill, and treating "the first tool call was
something else" as a non-trigger (as run_eval.py does) undercounts.

Usage:
    python scripts/probe_trigger.py evals/trigger/trigger-evals.json \
        --skill-dir . --out evals/trigger/results.json --runs 3
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_lock = threading.Lock()


def log(msg: str) -> None:
    with _lock:
        print(msg, file=sys.stderr, flush=True)


def skill_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return skill_dir.name


def build_project(skill_dir: Path, name: str) -> str:
    """A scratch project containing only this skill, so nothing else competes."""
    root = tempfile.mkdtemp(prefix="trigger-proj-")
    dest = Path(root) / ".claude" / "skills" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_dir, dest,
                    ignore=shutil.ignore_patterns(".git", "evals", "scripts", "dist", ".claude"))
    return root


def fired(query: str, name: str, project: str, model: str, timeout: int) -> bool | None:
    """True/False if measured, None if the run failed and should not be scored."""
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose",
           "--include-partial-messages", "--model", model, "--max-budget-usd", "0.60"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=project)
    except subprocess.TimeoutExpired:
        return None
    if not proc.stdout:
        return None

    saw_any_event = False
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        saw_any_event = True
        blob = ""
        if event.get("type") == "assistant":
            for item in event.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    blob = f"{item.get('name','')} {json.dumps(item.get('input', {}))}"
                    if name in blob:
                        return True
        elif event.get("type") == "stream_event":
            se = event.get("event", {})
            if se.get("type") == "content_block_delta":
                delta = se.get("delta", {})
                if name in delta.get("partial_json", ""):
                    return True
    return False if saw_any_event else None


def probe(item: dict, name: str, project: str, runs: int, model: str, timeout: int) -> dict:
    results = [fired(item["query"], name, project, model, timeout) for _ in range(runs)]
    valid = [r for r in results if r is not None]
    return {
        "query": item["query"],
        "should_trigger": item["should_trigger"],
        "triggers": sum(valid),
        "runs": len(valid),
        "invalid": len(results) - len(valid),
        # None, not 0 — a query with no valid runs was not measured, and calling
        # that "never triggered" is the same class of error this script exists
        # to avoid.
        "trigger_rate": (sum(valid) / len(valid)) if valid else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eval_set")
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--model", default="claude-opus-5")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    name = skill_name(skill_dir)
    project = build_project(skill_dir, name)
    items = json.loads(Path(args.eval_set).read_text())
    log(f"skill '{name}': {len(items)} queries x {args.runs} runs, project {project}")

    results, done = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(probe, i, name, project, args.runs, args.model, args.timeout): i
                   for i in items}
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            if done % 5 == 0 or done == len(items):
                log(f"  {done}/{len(items)}")
    shutil.rmtree(project, ignore_errors=True)

    scored = [r for r in results if r["trigger_rate"] is not None]
    pos = [r for r in scored if r["should_trigger"]]
    neg = [r for r in scored if not r["should_trigger"]]
    tpr = sum(r["trigger_rate"] for r in pos) / len(pos) if pos else None
    fpr = sum(r["trigger_rate"] for r in neg) / len(neg) if neg else None

    payload = {
        "skill": name, "model": args.model, "runs_per_query": args.runs,
        "unmeasured_queries": len(results) - len(scored),
        "positive_rate": tpr, "false_fire_rate": fpr,
        "gate_pass": bool(tpr is not None and fpr is not None and tpr >= 0.8 and fpr <= 0.10),
        "results": sorted(results, key=lambda r: (not r["should_trigger"], r["trigger_rate"] or 0)),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")

    log(f"\npositives {tpr:.2f} | false-fire {fpr:.2f} | gate "
        f"{'PASS' if payload['gate_pass'] else 'FAIL'} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
