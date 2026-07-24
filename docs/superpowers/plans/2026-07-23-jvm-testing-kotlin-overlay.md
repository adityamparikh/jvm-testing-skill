# JVM Testing Toolbox — Kotlin Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the `java-testing-toolbox` skill into `jvm-testing-toolbox` with first-class Kotlin coverage, treating mixed Java+Kotlin projects as the primary case.

**Architecture:** The skill is a router (`SKILL.md`) + progressive-disclosure references. Kotlin is added as a *sparse overlay*: inline swaps on the ~4 rows that genuinely differ, one dedicated "Kotlin on the JVM" table for Kotlin-only axes (coroutines/`Flow`), and a new `references/kotlin.md` for depth. Shared tables stay language-agnostic. The skill is renamed (directory + `name` + `description`) so Kotlin prompts route to it.

**Tech Stack:** Markdown skill files (`SKILL.md` frontmatter + Markdown tables), `references/*.md`. No application code.

## Global Constraints

- **Docs-only repo — there is no build system** (no `pom.xml` / `build.gradle`). "Verification" means `grep`/read checks + routing sanity, NOT a build or test run. Do not fabricate a build step.
- **Work happens on the existing branch `feat/jvm-testing-kotlin-overlay`** (design doc already committed there; PR #1 open). Do not branch again; do not commit to `main`.
- **Every commit uses sign-off + co-author trailer.** Use `git commit -s` and append verbatim:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- **Skill slug is `jvm-testing-toolbox`** everywhere (directory name, frontmatter `name`, README paths). The book *title* "Java Testing Toolbox" (with spaces) stays as-is in credit text — it is the source's name, not the slug.
- **"Beyond the book" framing:** MockK, Kotest, kotlinx-coroutines-test, Turbine, and Konsist are additions beyond Philip Riecks' (Java-framed) book. Every place they appear must signal this so the skill doesn't imply the book covers them.
- **Currency stamp stays `2026-07`** — do not bump it; new content is same-era.
- **Preserve existing style:** terse router rows (`| I need to… | Reach for | Tie-breaker / note |`), **bold** the default, one high-signal note per tool card.

---

### Task 1: Rename the skill (directory + identity + triggers)

Renames the skill and retargets its frontmatter so Kotlin prompts route to it. This is the atomic "make it the JVM skill" change.

**Files:**
- Rename: `.claude/skills/java-testing-toolbox/` → `.claude/skills/jvm-testing-toolbox/` (whole directory, via `git mv`)
- Modify: `.claude/skills/jvm-testing-toolbox/SKILL.md` (frontmatter `name` + `description`, H1 title)

**Interfaces:**
- Consumes: nothing (first task).
- Produces: the directory `.claude/skills/jvm-testing-toolbox/` and skill `name: jvm-testing-toolbox` that every later task and the README depend on.

- [ ] **Step 1: Verify current state (the "failing" check)**

Run: `ls .claude/skills/ && grep -n "^name:" .claude/skills/java-testing-toolbox/SKILL.md`
Expected: directory `java-testing-toolbox` exists; `name: java-testing-toolbox`.

- [ ] **Step 2: Rename the directory with git**

Run:
```bash
git mv .claude/skills/java-testing-toolbox .claude/skills/jvm-testing-toolbox
```

- [ ] **Step 3: Update the frontmatter `name`**

In `.claude/skills/jvm-testing-toolbox/SKILL.md`, change:
```
name: java-testing-toolbox
```
to:
```
name: jvm-testing-toolbox
```

- [ ] **Step 4: Replace the frontmatter `description` with the Kotlin-aware version**

Replace the entire `description: >-` block (lines currently ending "…handle JUnit 6 migration gotchas.") with:
```yaml
description: >-
  Use when choosing which JVM testing tool to reach for on a specific challenge
  in a Java and/or Kotlin project — picking a test framework, assertion library,
  mocking approach, or an HTTP / infrastructure / UI / performance / contract /
  architecture tool. Routes a testing problem to the right tool from Philip
  Riecks' "Java Testing Toolbox" (plus Kotlin-native additions) and flags the
  selection tie-breakers and pitfalls that generic knowledge misses. Triggers
  on: assert JSON or XML, mock an external HTTP API, integration test with a
  real database/broker/cloud, test asynchronous code, load-test or
  microbenchmark, contract-test microservices, enforce architecture rules,
  generate test data, judge test quality beyond coverage, decide between JUnit
  versions (4 vs 5 vs 6) and handle JUnit 6 migration gotchas, pick a
  Kotlin-idiomatic tool (MockK vs Mockito, Kotest, Konsist), mock a final Kotlin
  class, or test Kotlin coroutines/suspend functions and Flows
  (kotlinx-coroutines-test, Turbine).
```

- [ ] **Step 5: Update the H1 title**

Change:
```
# Java Testing Toolbox — tool selector
```
to:
```
# JVM Testing Toolbox — tool selector
```

- [ ] **Step 6: Verify the rename landed and no slug remnants in the skill dir**

Run:
```bash
ls .claude/skills/jvm-testing-toolbox/ && \
grep -n "^name: jvm-testing-toolbox" .claude/skills/jvm-testing-toolbox/SKILL.md && \
grep -rn "java-testing-toolbox" .claude/skills/ || echo "OK: no slug remnants in skill dir"
```
Expected: new dir listed; `name:` matches; the recursive grep prints nothing (so the `|| echo OK` fires). The book title "Java Testing Toolbox" (spaces) may still appear — that's fine; only the hyphenated slug matters.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/
git commit -s -m "Rename java-testing-toolbox skill to jvm-testing-toolbox

Retarget frontmatter name + description so Kotlin prompts (MockK, Kotest,
coroutines, Flow, Konsist, final-class mocking) route here. Directory,
name, and H1 updated; book title unchanged in prose.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Add Kotlin tool cards to `references/tool-cards.md`

Adds one high-signal card per Kotlin tool, matching the existing card style.

**Files:**
- Modify: `.claude/skills/jvm-testing-toolbox/references/tool-cards.md` (append a new section at end of file, after the "Architecture & quality" section)

**Interfaces:**
- Consumes: renamed dir from Task 1.
- Produces: cards for **MockK, Kotest, kotlinx-coroutines-test, Turbine, Konsist** that `SKILL.md` (Task 5) points into.

- [ ] **Step 1: Verify the tools are absent today**

Run: `grep -n "MockK\|Kotest\|Turbine\|Konsist\|coroutines-test" .claude/skills/jvm-testing-toolbox/references/tool-cards.md || echo "OK: absent"`
Expected: prints `OK: absent`.

- [ ] **Step 2: Append the Kotlin section**

At the end of `references/tool-cards.md`, add:
```markdown

## Kotlin (beyond the book)

- **MockK** — idiomatic Kotlin mocking. Note: built for Kotlin's defaults — mocks
  `final` classes with no config, plus `object`s (`mockkObject`), static/top-level
  and extension functions (`mockkStatic`), and coroutines (`coEvery { } returns`,
  `coVerify { }`). `relaxed = true` / `@RelaxedMockK` avoids stubbing every call.
  Don't run MockK and Mockito in the same module — pick one.
- **Kotest** — Kotlin-native framework + assertions. Note: multiple spec styles
  (`StringSpec`, `BehaviorSpec`, `FunSpec`), first-class property testing
  (`checkAll`, `Arb`), and `shouldBe`/`shouldContain` matchers usable even from
  JUnit (add `kotest-assertions-core` alone). Optional — JUnit 6 runs Kotlin fine;
  adopt Kotest for spec styles / property testing, not by default.
- **kotlinx-coroutines-test** — test `suspend`/coroutine code. Note: `runTest { }`
  uses a virtual-time scheduler so `delay()` is skipped and tests stay
  deterministic. `StandardTestDispatcher` queues coroutines (advance with
  `advanceUntilIdle()`/`runCurrent()`); `UnconfinedTestDispatcher` runs them
  eagerly. Inject dispatchers into production code — hardcoded `Dispatchers.IO`
  can't be swapped for a `TestDispatcher`.
- **Turbine** — assert on `Flow` emissions. Note: `flow.test { awaitItem();
  awaitComplete() }` **fails if any emitted item goes unconsumed**, catching
  over-emission a plain `toList()` collect would hide. `awaitError()` for
  failures; `cancelAndIgnoreRemainingEvents()` for infinite flows.
- **Konsist** — Kotlin architecture/consistency tests. Note: parses Kotlin *source*
  via the compiler, so it sees top-level functions, extension functions, and
  package structure that ArchUnit's *bytecode* view misses. Rules run as
  JUnit/Kotest tests. Use alongside ArchUnit (stronger on JVM-level layering), not
  necessarily instead.
```

- [ ] **Step 3: Verify all five cards present**

Run: `grep -c "^- \*\*MockK\*\*\|^- \*\*Kotest\*\*\|^- \*\*kotlinx-coroutines-test\*\*\|^- \*\*Turbine\*\*\|^- \*\*Konsist\*\*" .claude/skills/jvm-testing-toolbox/references/tool-cards.md`
Expected: `5`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/tool-cards.md
git commit -s -m "Add Kotlin tool cards (MockK, Kotest, coroutines-test, Turbine, Konsist)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Add Kotlin pitfalls to `references/pitfalls.md`

**Files:**
- Modify: `.claude/skills/jvm-testing-toolbox/references/pitfalls.md` (append a "Kotlin pitfalls" section at end of file)

**Interfaces:**
- Consumes: renamed dir from Task 1.
- Produces: Kotlin gotchas the `SKILL.md` cross-cutting reminders (Task 5) and `references/kotlin.md` (Task 4) reinforce.

- [ ] **Step 1: Verify absent**

Run: `grep -n "Kotlin pitfalls" .claude/skills/jvm-testing-toolbox/references/pitfalls.md || echo "OK: absent"`
Expected: `OK: absent`.

- [ ] **Step 2: Append the section**

At the end of `references/pitfalls.md`, add:
```markdown

## Kotlin pitfalls

- **Mockito fights Kotlin's defaults.** Kotlin classes/methods are `final` unless
  `open`, so plain Mockito can't mock them without the **inline mock-maker**
  (`mockito-inline` / the `mock-maker-inline` resource). Its `any()` can also
  return `null` into a non-null Kotlin parameter and throw. Use **MockK**, or add
  **mockito-kotlin** (`whenever`, `mock()`, nullable-safe matchers). Don't run
  both mockers in one module.
- **Coroutine tests must not use real time.** Use `runTest { }` (virtual time)
  with an injected `TestDispatcher` — not `runBlocking` + real `delay`, and never
  `Thread.sleep`. Production code must **take its dispatcher as a parameter**;
  hardcoded `Dispatchers.IO`/`Main` can't be replaced, so the test can't control
  scheduling. Choose `StandardTestDispatcher` (manual `advanceUntilIdle()`) vs
  `UnconfinedTestDispatcher` (eager) deliberately.
- **`Flow` tests silently pass without Turbine.** Collecting to a list and
  asserting size can miss extra/late emissions. **Turbine**'s `test { }` fails on
  any unconsumed item, so over-emission is caught.
- **Kotest vs JUnit is a choice, not a default.** JUnit 6 runs Kotlin (including
  `suspend` test methods). Adopt Kotest for its spec styles / property testing —
  don't assume a Kotlin project must drop JUnit.
- **Data classes change what you assert.** `equals`/`hashCode` are generated, so
  assert whole-object equality (`shouldBe`, AssertJ `isEqualTo`) instead of
  field-by-field — but `copy()` is shallow, so deep structures still need care.
```

- [ ] **Step 3: Verify present**

Run: `grep -n "Kotlin pitfalls\|Mockito fights Kotlin\|silently pass without Turbine" .claude/skills/jvm-testing-toolbox/references/pitfalls.md`
Expected: three matching lines.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/pitfalls.md
git commit -s -m "Add Kotlin pitfalls (Mockito+final classes, coroutine time, Flow, Kotest choice)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Create `references/kotlin.md` (depth notes)

**Files:**
- Create: `.claude/skills/jvm-testing-toolbox/references/kotlin.md`

**Interfaces:**
- Consumes: renamed dir from Task 1.
- Produces: the file `references/kotlin.md` that `SKILL.md` "How to use" step (Task 5) links to for Kotlin depth.

- [ ] **Step 1: Verify absent**

Run: `ls .claude/skills/jvm-testing-toolbox/references/kotlin.md 2>/dev/null || echo "OK: absent"`
Expected: `OK: absent`.

- [ ] **Step 2: Create the file with this exact content**

```markdown
# Kotlin testing — depth notes

**Last verified: 2026-07.** Version-sensitive claims follow the Currency rule in
`SKILL.md`. These tools are **beyond Philip Riecks' (Java-framed) book** — added
because real JVM projects mix Java and Kotlin.

Load this once routing has landed on a Kotlin-specific tool. For the quick
decision, use the "Kotlin on the JVM" table in `SKILL.md`.

## MockK vs Mockito (+ mockito-kotlin)

- **MockK** is built for Kotlin: it mocks `final` classes with no extra config,
  and handles `object` singletons (`mockkObject`), static/top-level and extension
  functions (`mockkStatic`), and coroutines (`coEvery { } returns …`,
  `coVerify { }`). `relaxed = true` (or `@RelaxedMockK`) returns sensible defaults
  so you don't stub every call; use a strict mock when unstubbed calls should fail.
- **Mockito in Kotlin** needs the **inline mock-maker** to mock final types
  (Kotlin's default), and its Java-oriented matchers can push `null` into
  non-null Kotlin parameters. **mockito-kotlin** smooths this over (`whenever`,
  `mock<T>()`, `argumentCaptor`, nullable-safe matchers).
- **Rule:** one mocker per module. Mixing MockK and Mockito on the same types
  causes confusing failures and doubles the mental model.
- **When to keep Mockito:** a mostly-Java codebase where a few tests happen to be
  Kotlin, or heavy `@MockBean`/Spring-Mockito integration. **Reach for MockK** in
  Kotlin-first modules and anything coroutine-heavy.

## Coroutine testing: kotlinx-coroutines-test

- `runTest { }` installs a **virtual-time** scheduler: `delay()` is skipped, so a
  test of a 30-second timeout runs instantly and deterministically.
- **Dispatcher choice:**
  - `StandardTestDispatcher` — new coroutines are **queued**, not run, until you
    advance the scheduler (`advanceUntilIdle()`, `advanceTimeBy(ms)`,
    `runCurrent()`). Best when you want to assert intermediate states.
  - `UnconfinedTestDispatcher` — new coroutines start **eagerly** and run until
    their first suspension. Best for simple "fire and assert the result" tests.
- **Design for testability:** production code must take its `CoroutineDispatcher`
  as a constructor/parameter (or use an injected scope). Hardcoded
  `Dispatchers.IO`/`Dispatchers.Main` can't be replaced with a `TestDispatcher`,
  so scheduling can't be controlled. For `Dispatchers.Main` in unit tests, set
  `Dispatchers.setMain(testDispatcher)` in setup and `Dispatchers.resetMain()` in
  teardown.

## Flow testing: Turbine

- `flow.test { … }` collects the flow inside a scope and **requires every emission
  to be consumed** — `awaitItem()`, `awaitComplete()`, `awaitError()`. If the flow
  emits more than the test consumes, the block fails; a plain `toList()` collect
  would silently pass.
- For infinite/hot flows, end with `cancelAndIgnoreRemainingEvents()`.
- Combine with virtual time (`runTest`) when the flow uses `delay`/`debounce`.

## Kotest — when it earns its place

- **Spec styles** (`StringSpec`, `FunSpec`, `BehaviorSpec`, `DescribeSpec`) give
  BDD-ish structure without JUnit's annotations.
- **Property testing** (`checkAll`, `Arb` generators) is first-class — often the
  main reason to bring Kotest into an otherwise-JUnit project.
- **Assertions are separable:** add only `kotest-assertions-core` for
  `shouldBe`/`shouldContain`/`shouldThrow` and keep running under JUnit.
- **Don't reflexively replace JUnit** — JUnit 6 already runs Kotlin (and `suspend`
  test methods). Adopt Kotest for spec styles or property testing, not as a
  default swap.

## Konsist — Kotlin architecture rules

- Parses **Kotlin source** via the compiler, so rules can target top-level
  functions, extension functions, visibility, and package layout that ArchUnit
  (which reads **bytecode**) can't always see.
- Rules run as ordinary JUnit/Kotest tests, same as ArchUnit.
- **ArchUnit vs Konsist:** ArchUnit is stronger for JVM-level layering/cycles
  across a mixed Java+Kotlin codebase; Konsist for Kotlin-idiom rules (e.g.
  "every use case is an `internal` class", "no top-level mutable state"). They
  coexist.
```

- [ ] **Step 3: Verify the file exists with all five headings**

Run: `grep -c "^## " .claude/skills/jvm-testing-toolbox/references/kotlin.md`
Expected: `5` (MockK vs Mockito, Coroutine testing, Flow testing, Kotest, Konsist).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/kotlin.md
git commit -s -m "Add references/kotlin.md depth notes (MockK, coroutines, Flow, Kotest, Konsist)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Make `SKILL.md` router Kotlin-aware

The core routing change: language-agnostic framing, inline swaps on the rows that differ, the new "Kotlin on the JVM" table, and Kotlin cross-cutting reminders. Referenced files (tool-cards, pitfalls, kotlin.md) already exist from Tasks 2–4.

**Files:**
- Modify: `.claude/skills/jvm-testing-toolbox/SKILL.md` (body only; frontmatter/title already done in Task 1)

**Interfaces:**
- Consumes: `references/kotlin.md` (Task 4), Kotlin cards (Task 2), Kotlin pitfalls (Task 3).
- Produces: the `### Kotlin on the JVM` section heading that the README (Task 6) references.

- [ ] **Step 1: Verify current body state**

Run: `grep -n "Assume idiomatic use\|## How to use\|### Mocking & stubbing\|### Architecture & test quality\|## Cross-cutting reminders" .claude/skills/jvm-testing-toolbox/SKILL.md`
Expected: five anchor lines found (these are the edit anchors below).

- [ ] **Step 2: Update the intro line to name Kotlin tools**

Change:
```
(JUnit 5, Mockito, AssertJ) is already known.
```
to:
```
(JUnit 5/6, Mockito, AssertJ; MockK and Kotest on Kotlin) is already known.
```

- [ ] **Step 3: Add the "beyond the book" note to the source paragraph**

After the sentence ending `github.com/rieckpil/java-testing-ecosystem`.` add a new sentence in the same paragraph:
```
 Kotlin-native tools (MockK, Kotest, kotlinx-coroutines-test, Turbine, Konsist)
are additions **beyond the book**, included because real JVM projects mix Java
and Kotlin.
```

- [ ] **Step 4: Add the language-agnostic framing to "How to use this skill"**

After the numbered list in `## How to use this skill` (after the "Only pull deeper detail…" item), add:
```markdown

**Java or Kotlin?** These tables apply to both. Where Kotlin has an idiomatic
swap, the row's note names it (**Kotlin:** …); Kotlin-only concerns (coroutines,
`Flow`) are in the **Kotlin on the JVM** section below. For Kotlin depth, open
`references/kotlin.md`.
```

- [ ] **Step 5: Inline swap — Mockito row (Mocking & stubbing table)**

In the Mockito row, append to the tie-breaker/note cell (after "…`thenAnswer`, `verify`."):
```
 **Kotlin:** prefer **MockK** (final-by-default classes, `object`s, extension fns, and coroutines via `coEvery`/`coVerify`); Mockito needs `mockito-kotlin` + the inline mock-maker.
```

- [ ] **Step 6: Inline swap — Test frameworks table (add Kotest row)**

Add a new row at the end of the "Test frameworks" table, after the Spock row:
```markdown
| Kotlin-native spec styles or property testing | Kotest | Kotlin framework: `StringSpec`/`BehaviorSpec`, `checkAll` property testing, `shouldBe` matchers. Optional — JUnit 6 + AssertJ run Kotlin fine. **Beyond the book.** |
```

- [ ] **Step 7: Inline swap — AssertJ row (Assertion libraries table)**

In the AssertJ row, append to the note cell (after "…custom `AbstractAssert` for domain types."):
```
 **Kotlin:** Kotest matchers (`x shouldBe y`) / Strikt are idiomatic alternatives; AssertJ still works.
```

- [ ] **Step 8: Inline swap — ArchUnit row (Architecture & test quality table)**

In the ArchUnit row, append to the note cell (after "…must take a `Clock`\"."):
```
 **Kotlin:** **Konsist** parses Kotlin source, so it catches top-level/extension-fn rules ArchUnit's bytecode view misses.
```

- [ ] **Step 9: Add the "Kotlin on the JVM" section**

Immediately before `## Cross-cutting reminders`, insert:
```markdown
### Kotlin on the JVM

Most tables above apply to Kotlin unchanged. These are the Kotlin-**specific**
choices — a swap for a shared concern, plus axes with no Java equivalent. All are
**beyond Riecks' (Java-framed) book**; depth in `references/kotlin.md`.

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock in idiomatic Kotlin | **MockK** | Final-by-default classes, `object`s, extension/top-level fns, and coroutines (`coEvery`/`coVerify`) native. Mockito needs `mockito-kotlin` + inline mock-maker. Don't mix the two mockers in one module. |
| Test `suspend` functions / coroutine logic | **kotlinx-coroutines-test** | `runTest { }` drives virtual time; advance with `advanceUntilIdle()` / `runCurrent()`. Inject dispatchers — don't hardcode `Dispatchers.IO` — so a `TestDispatcher` can replace them. |
| Assert on values a `Flow` emits | **Turbine** | `flow.test { awaitItem(); awaitComplete() }` — fails on unconsumed items, unlike a plain `toList()` collect. Pairs with any assertion lib. |
| Framework / assertions, Kotlin-native | **Kotest** | Spec styles + property testing + `shouldBe`. Optional — JUnit 6 + AssertJ work fine in Kotlin. |
| Kotlin-aware architecture rules | **Konsist** | Understands Kotlin source (top-level/extension fns) ArchUnit can miss; coexists with ArchUnit. |

```

- [ ] **Step 10: Add Kotlin cross-cutting reminders**

In `## Cross-cutting reminders`, add two bullets (after the "Awaitility over `Thread.sleep`" bullet):
```markdown
- **Kotlin: MockK over Mockito** for `object`s, final classes, extension fns, and
  coroutines — or add `mockito-kotlin` + the inline mock-maker. Don't mix the two
  mockers in one module.
- **Kotlin coroutines: `runTest` + an injected `TestDispatcher`**, never real
  delays or `Thread.sleep`; use **Turbine** for `Flow`.
```

- [ ] **Step 11: Verify all Kotlin routing content is present**

Run:
```bash
grep -n "Kotlin on the JVM\|Java or Kotlin?\|MockK\|Kotest\|kotlinx-coroutines-test\|Turbine\|Konsist\|references/kotlin.md" .claude/skills/jvm-testing-toolbox/SKILL.md
```
Expected: matches for the new section heading, the framing line, all five tool names, and the `references/kotlin.md` link.

- [ ] **Step 12: Verify table integrity (no broken Markdown rows)**

Read the "Test frameworks", "Mocking & stubbing", "Assertion libraries", "Architecture & test quality", and new "Kotlin on the JVM" tables. Confirm every row has the same pipe-column count as its header (3 columns). Fix any row that doesn't.

- [ ] **Step 13: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/SKILL.md
git commit -s -m "Make SKILL.md router Kotlin-aware (framing, inline swaps, Kotlin section)

Language-agnostic framing + inline Kotlin swaps on the rows that differ
(Mockito->MockK, ArchUnit->Konsist, Kotest as framework/assertion option),
a dedicated 'Kotlin on the JVM' table for coroutine/Flow testing, and
Kotlin cross-cutting reminders. Links to references/kotlin.md.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Update `README.md`

Reflect the rename (with an old-name note so references resolve), the new file, and Kotlin coverage.

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: the `jvm-testing-toolbox` slug (Task 1), `references/kotlin.md` (Task 4), the "Kotlin on the JVM" coverage (Task 5).
- Produces: nothing downstream (final content task before verification).

- [ ] **Step 1: Update the H1 title**

Change:
```
# Java Testing Toolbox — an AI agent skill
```
to:
```
# JVM Testing Toolbox — an AI agent skill
```

- [ ] **Step 2: Add a rename note under the H1**

Immediately after the H1, add:
```markdown

> **Renamed from `java-testing-toolbox`.** The skill now covers Kotlin too, for
> mixed Java+Kotlin projects; its directory and skill name are
> `jvm-testing-toolbox`.
```

- [ ] **Step 3: Broaden the intro sentence**

Change:
```
tools (Claude Code, Cursor, Copilot, …) **pick the right Java/JVM testing tool
for a given challenge**
```
to:
```
tools (Claude Code, Cursor, Copilot, …) **pick the right JVM testing tool for a
given challenge in a Java and/or Kotlin project**
```

- [ ] **Step 4: Update the "What's inside" tree**

Replace the tree block with:
```
.claude/skills/jvm-testing-toolbox/
├── SKILL.md                 # the router: problem → tool decision tables
└── references/
    ├── tool-cards.md        # one card per tool: purpose + the one high-signal note
    ├── pitfalls.md          # cross-cutting gotchas + tie-breaker rationale
    └── kotlin.md            # Kotlin depth: MockK, coroutines, Flow, Kotest, Konsist
```

- [ ] **Step 5: Add a Kotlin row to the Coverage table**

After the "Architecture & quality" row, add:
```markdown
| Kotlin (beyond the book) | MockK, Kotest, kotlinx-coroutines-test, Turbine, Konsist |
```
Then, after the coverage table's trailing paragraph about JUnit 6, add:
```markdown

Kotlin-native tools (MockK, Kotest, kotlinx-coroutines-test, Turbine, Konsist)
are **additions beyond the book's 30 Java tools**, because real JVM projects
frequently mix Java and Kotlin.
```

- [ ] **Step 6: Update the Usage path**

Change `Drop the `.claude/skills/java-testing-toolbox/` directory` to
`Drop the `.claude/skills/jvm-testing-toolbox/` directory`.

- [ ] **Step 7: Verify README updated and no stale slug except the rename note**

Run:
```bash
grep -n "jvm-testing-toolbox\|Renamed from\|Kotlin (beyond the book)\|kotlin.md" README.md && \
grep -n "java-testing-toolbox" README.md
```
Expected: new-slug lines present; the only `java-testing-toolbox` hit is inside the "Renamed from" note.

- [ ] **Step 8: Commit**

```bash
git add README.md
git commit -s -m "Update README for jvm-testing-toolbox rename + Kotlin coverage

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Final verification sweep

Confirms coherence, no stale references, and routing sanity across the whole change.

**Files:**
- None modified (verification + optional push).

**Interfaces:**
- Consumes: all prior tasks.
- Produces: a verified branch ready for PR review.

- [ ] **Step 1: No stale slug anywhere except intended notes**

Run:
```bash
grep -rn "java-testing-toolbox" . --include="*.md" | grep -v "docs/superpowers/"
```
Expected: the ONLY hit is the README "Renamed from `java-testing-toolbox`" note. (Anything under `docs/superpowers/` is historical planning and is allowed.) If any skill file still contains the old slug, fix it and re-commit.

- [ ] **Step 2: Frontmatter sanity**

Run: `grep -n "^name:\|^description:" .claude/skills/jvm-testing-toolbox/SKILL.md`
Expected: `name: jvm-testing-toolbox`; description present. Confirm the description block is valid YAML (single `>-` block, consistent indentation).

- [ ] **Step 3: Reference links resolve**

Run: `ls .claude/skills/jvm-testing-toolbox/references/`
Expected: `tool-cards.md  pitfalls.md  kotlin.md`. Confirm `SKILL.md` references each by the name it uses.

- [ ] **Step 4: Routing sanity (manual read)**

Read `SKILL.md` top-to-bottom once. Confirm: (a) a Java-only reader sees no Kotlin noise except the ~4 annotated rows + the Kotlin section; (b) a Kotlin prompt ("mock a final Kotlin class", "test a `suspend` function", "test a `Flow`") has an obvious landing row; (c) every Kotlin tool named in a table has a matching card in `tool-cards.md`.

- [ ] **Step 5: Push the branch (updates PR #1)**

```bash
git push
```
Then print the PR URL: `https://github.com/adityamparikh/java-testing-skill/pull/1`

## Self-Review

**Spec coverage** (checked against `docs/superpowers/specs/2026-07-23-jvm-testing-kotlin-overlay-design.md`):
- Frame shared tables language-agnostic → Task 5 Step 4. ✅
- Inline swaps on Mockito / ArchUnit / frameworks+assertions → Task 5 Steps 5–8. ✅
- New "Kotlin on the JVM" section (coroutines, Flow, MockK, Konsist) → Task 5 Step 9. ✅
- New `references/kotlin.md` → Task 4. ✅
- Rename dir + name + description + old-name note → Task 1 + Task 6 Step 2. ✅
- tool-cards additions (MockK, Kotest, coroutines-test, Turbine, Konsist) → Task 2. ✅
- pitfalls additions → Task 3. ✅
- README name + coverage → Task 6. ✅
- Decisions locked: coroutine depth (route + gotcha in tables, nuance in kotlin.md) → Tasks 4/5; "beyond the book" framing → Tasks 2,4,5,6. ✅
- Out-of-scope respected: no swap column, no per-language split, no build-tool guidance, Strikt/Kluent only one-line mentions → confirmed across tasks. ✅

**Placeholder scan:** No TBD/TODO; every edit shows literal content and an anchor. ✅

**Type/name consistency:** Slug `jvm-testing-toolbox` used identically in Tasks 1, 6, 7; section heading `Kotlin on the JVM` produced in Task 5 Step 9 and referenced in Task 5 Steps 4/10 and README; file `references/kotlin.md` created in Task 4 and linked in Task 5 Step 4 + README Step 4. ✅
