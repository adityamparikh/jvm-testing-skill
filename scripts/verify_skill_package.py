#!/usr/bin/env python3
"""Verify a skill package is internally consistent before it ships.

The failure this exists to catch: a SKILL.md that tells the model to go read
`references/foo.md` in a package that does not ship `references/foo.md`. The
model follows the pointer, finds nothing, and silently loses the entire depth
layer of the skill. Nothing in the normal authoring loop surfaces this — the
repo is fine, only the *packaged* or *installed* copy is broken.

Checks:
  1. SKILL.md exists and has `name` and `description` in YAML frontmatter.
  2. Every bundled-resource pointer (references/, scripts/, assets/) mentioned
     in any markdown file in the package resolves to a file that exists.
  3. Every file under references/ is reachable from SKILL.md, directly or
     transitively. An unreachable reference file is dead weight: it costs
     repository maintenance but the model is never routed to it.

Usage:
    python scripts/verify_skill_package.py [SKILL_DIR]

SKILL_DIR defaults to the repo root. Exits 0 if clean, 1 if any check fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Pointers look like `references/foo.md`, scripts/bar.py, "assets/baz.html".
# Match the bundled-resource directories the skill spec defines, and stop at
# whitespace or a closing delimiter.
POINTER_RE = re.compile(r"(?:references|scripts|assets)/[A-Za-z0-9._/-]+")

# A fenced code block may legitimately show a path that does not exist (an
# example layout, a command the *user* is told to run). Strip fences first so
# illustrative paths do not produce false failures.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# A skill may deliberately hand off to a *different* skill's reference file:
#   "see the `spring-boot` skill's `references/observability.md`"
# That path is not ours to resolve, so it must not be checked against this
# package — but it is worth reporting, because a handoff to a skill the user
# has not installed fails just as silently as a dangling local pointer.
EXTERNAL_RE = re.compile(
    r"skill'?s?\s+`((?:references|scripts|assets)/[A-Za-z0-9._/-]+)`",
    re.IGNORECASE,
)

RESOURCE_DIRS = ("references", "scripts", "assets")


def strip_code_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def find_pointers(text: str) -> tuple[set[str], set[str]]:
    """Return (local pointers to verify, external cross-skill pointers)."""
    body = strip_code_fences(text)
    external = set(EXTERNAL_RE.findall(body))
    local = set(POINTER_RE.findall(body)) - external
    return local, external


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], list[str]]:
    """Return (frontmatter fields, errors). Only top-level scalar keys."""
    text = skill_md.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---"):
        return {}, [f"{skill_md.name}: missing YAML frontmatter (no leading '---')"]

    end = text.find("\n---", 3)
    if end == -1:
        return {}, [f"{skill_md.name}: frontmatter is never closed"]

    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        # Only capture top-level keys; continuation lines of a folded scalar
        # are indented and are not keys.
        if line[:1].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()

    for required in ("name", "description"):
        if required not in fields:
            errors.append(f"{skill_md.name}: frontmatter is missing required key '{required}'")

    return fields, errors


def reachable_from_skill_md(skill_dir: Path) -> set[str]:
    """Pointers reachable from SKILL.md, following reference files transitively."""
    seen: set[str] = set()
    queue = [skill_dir / "SKILL.md"]

    while queue:
        current = queue.pop()
        if not current.is_file():
            continue
        local, _ = find_pointers(current.read_text(encoding="utf-8"))
        for pointer in local:
            if pointer in seen:
                continue
            seen.add(pointer)
            target = skill_dir / pointer
            if target.is_file() and target.suffix == ".md":
                queue.append(target)

    return seen


def discover_skill_dir(repo_root: Path) -> Path | None:
    """Locate the skill package within a repo.

    Two layouts are in use: SKILL.md at the repo root (java-performance-skill)
    and SKILL.md under .claude/skills/<name>/ (jvm-testing-skill). Handle both
    so the same script drops into either repo unchanged.
    """
    if (repo_root / "SKILL.md").is_file():
        return repo_root
    candidates = sorted(repo_root.glob(".claude/skills/*/SKILL.md"))
    return candidates[0].parent if len(candidates) == 1 else None


def main() -> int:
    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1]).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent
        found = discover_skill_dir(repo_root)
        if found is None:
            print(f"FAIL  could not locate a unique SKILL.md under {repo_root}")
            print("      pass the skill directory explicitly")
            return 1
        skill_dir = found

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"FAIL  no SKILL.md at {skill_dir}")
        return 1

    errors: list[str] = []
    fields, frontmatter_errors = parse_frontmatter(skill_md)
    errors.extend(frontmatter_errors)

    # Check 2 — every local pointer in every markdown file resolves.
    dangling: list[tuple[str, str]] = []
    external: list[tuple[str, str]] = []
    for md in sorted(skill_dir.rglob("*.md")):
        if ".git" in md.parts:
            continue
        rel = md.relative_to(skill_dir)
        local, cross_skill = find_pointers(md.read_text(encoding="utf-8"))
        for pointer in sorted(local):
            if not (skill_dir / pointer).exists():
                dangling.append((str(rel), pointer))
        for pointer in sorted(cross_skill):
            external.append((str(rel), pointer))

    # Check 3 — every shipped reference file is reachable from SKILL.md.
    reachable = reachable_from_skill_md(skill_dir)
    orphans: list[str] = []
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref in sorted(refs_dir.rglob("*")):
            if not ref.is_file():
                continue
            rel = str(ref.relative_to(skill_dir))
            if rel not in reachable:
                orphans.append(rel)

    name = fields.get("name", skill_dir.name)
    shipped = sum(1 for d in RESOURCE_DIRS if (skill_dir / d).is_dir())
    print(f"Skill: {name}  ({skill_dir})")
    print(f"  bundled resource dirs shipped: {shipped}/{len(RESOURCE_DIRS)}")
    print(f"  pointers reachable from SKILL.md: {len(reachable)}")

    if dangling:
        print(f"\nFAIL  {len(dangling)} pointer(s) reference a file this package does not ship:")
        for source, pointer in dangling:
            print(f"    {source} -> {pointer}")
        print("\n  The model will follow these and find nothing. Either ship the file")
        print("  or remove the pointer.")
        errors.append("dangling pointers")

    if orphans:
        print(f"\nWARN  {len(orphans)} reference file(s) unreachable from SKILL.md:")
        for orphan in orphans:
            print(f"    {orphan}")
        print("\n  Nothing routes the model to these, so they are never loaded.")

    if external:
        print(f"\nNOTE  {len(external)} cross-skill pointer(s), not verified here:")
        for source, pointer in external:
            print(f"    {source} -> {pointer}")
        print("\n  These resolve only if the companion skill is installed. A handoff")
        print("  to a skill the user does not have fails as silently as a dangling path.")

    for error in frontmatter_errors:
        print(f"FAIL  {error}")

    if errors:
        return 1

    print("\nOK  package is internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
