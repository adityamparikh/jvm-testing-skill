# JVM Testing Toolbox — Kotlin Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the `java-testing-toolbox` skill into `jvm-testing-toolbox` with first-class Kotlin coverage, treating mixed Java+Kotlin projects as the primary case.

**Architecture:** The skill is a router (`SKILL.md`) + progressive-disclosure references. Kotlin is added as a *sparse overlay*: inline swaps on the ~4 rows that genuinely differ, one dedicated "Kotlin on the JVM" table for Kotlin-only axes (coroutines/`Flow`), and a new `references/kotlin.md` for depth. Shared tables stay language-agnostic. The skill is renamed (directory + `name` + `description`) so Kotlin prompts route to it.

**Tech Stack:** Markdown skill files (`SKILL.md` frontmatter + Markdown tables), `references/*.md`. No application code.

## Global Constraints

- **Docs-only repo — there is no build system** (no `pom.xml` / `build.gradle`). "Verification" means `grep`/read checks + routing sanity, NOT a build or test run. Do not fabricate a build step.
- **Work happens on the existing branch `feat/jvm-testing-kotlin-overlay`** (design doc already committed there; PR #1 open). Do not branch again; do not commit to `main`.
- **Every commit uses sign-off + co-author trailer.** Use `git commit -s` and append verbatim:
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
- **Skill slug is `jvm-testing-toolbox`** everywhere (directory name, frontmatter `name`, README paths). The book *title* "Java Testing Toolbox" (with spaces) stays as-is in credit text — it is the source's name, not the slug.
- **"Beyond the book" framing:** MockK, kotlinx-coroutines-test, Turbine, and Kotest Property are additions beyond Philip Riecks' (Java-framed) book. Every place they appear must signal this so the skill doesn't imply the book covers them — **including README's `## Credit` section** (Task 6), which today claims every tool and pitfall is distilled from the book.
- **One engine (Jupiter).** JUnit Jupiter is the sole test engine for the module: one runner, one report, one CI config. Libraries may differ per file; engines may not. Kotest enters as a **library only** (assertions + property testing callable from a Jupiter `@Test`), never for its spec styles. No tool that requires a second engine is recommended — this is why jqwik is out of scope.
- **Currency stamp stays `2026-07`** — do not bump it. **But the stamp is a promise that the content under it was checked:** every content task below ends with a fact-check step that spot-checks its new version-sensitive claims against current release notes. A `grep` presence check is not verification. Facts already verified for this plan are listed under "Verified facts" below — do not re-derive them, but do re-check anything you add beyond them.
- **Konsist is out of scope.** ArchUnit reads bytecode and already runs on Kotlin; a second architecture tool isn't justified in a skill whose value is fewer, better-defended choices. Do not add Konsist cards, rows, or triggers.
- **Preserve existing style:** terse router rows (`| I need to… | Reach for | Tie-breaker / note |`), **bold** the default, one high-signal note per tool card.

## Verified facts (checked 2026-07-29 — do not re-derive)

These were wrong or unverified in the first draft of this plan. Sources checked:

- **Mockito 5.0.0 made the inline mock-maker the default in `mockito-core`.** Kotlin's
  final-by-default classes mock with **no extra dependency and no `mock-maker-inline`
  resource file**. The separate `mockito-inline` artifact stopped being published after
  5.2. Any claim that Mockito "can't mock Kotlin classes without the inline mock-maker"
  describes Mockito 4 and is stale.
- **`mockito-kotlin` can stub `suspend` functions** via `onBlocking { }` /
  `wheneverBlocking`. It has real rough edges — custom *suspending* answers (delay,
  indefinite suspension) and value-class boxing are awkward — but "Mockito cannot stub
  suspend functions" is false. MockK's advantage is ergonomics and advanced cases, not
  raw capability.
- **jqwik is excluded, and the reasons are worth recording.** It registers its own
  JUnit Platform engine (a second engine, breaking the one-engine rule); it is in
  **pure maintenance mode** — no feature work without sponsorship, only dependency
  updates and critical fixes; and since **v1.10 it ships an Anti-AI Usage Clause**.
  A skill whose only consumer is an AI coding agent should not route to it. Property
  testing is therefore Kotlin-side only, via `kotest-property`.
- **Kotest's assertions and property modules are separable.** `kotest-assertions-core`
  and `kotest-property` work inside a Jupiter `@Test` without the Kotest engine.
- **JUnit 6 natively supports Kotlin `suspend` test functions** (needs Java 17+ /
  Kotlin 2.2+).
- **PIT mutates Kotlin's compiler-generated `Intrinsics` null checks**, flooding reports
  with `removed call to kotlin/jvm/internal/Intrinsics::… → SURVIVED` false positives.
  The option that suppresses them also stops mutating any statement containing a null
  check — including real business logic. This is a genuine mixed-module trap.

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
  in a Java and/or Kotlin project — including when both languages share one
  module and source set. Covers picking a test framework, assertion library,
  mocking approach, or an HTTP / infrastructure / UI / performance / contract /
  architecture tool. Routes a testing problem to the right tool from Philip
  Riecks' "Java Testing Toolbox" (plus Kotlin-native additions) and flags the
  selection tie-breakers and pitfalls that generic knowledge misses. Triggers
  on: assert JSON or XML, mock an external HTTP API, integration test with a
  real database/broker/cloud, test asynchronous code, load-test or
  microbenchmark, contract-test microservices, enforce architecture rules,
  generate test data, judge test quality beyond coverage, decide between JUnit
  versions (4 vs 5 vs 6) and handle JUnit 6 migration gotchas, choose between
  MockK and Mockito on Kotlin, mock a Kotlin `object` or extension function,
  test Kotlin coroutines/suspend functions and Flows (kotlinx-coroutines-test,
  Turbine), write property-based tests in Kotlin (Kotest Property), or fix
  Java/Kotlin test interop problems in a mixed source set.
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

Retarget frontmatter name + description so Kotlin prompts (MockK, coroutines,
Flow, property testing, mixed-source-set interop) route here. Directory,
name, and H1 updated; book title unchanged in prose.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Add Kotlin + property-testing tool cards to `references/tool-cards.md`

Adds one high-signal card per new tool, matching the existing card style.

**Files:**
- Modify: `.claude/skills/jvm-testing-toolbox/references/tool-cards.md` (append a new section at end of file, after the "Architecture & quality" section)

**Interfaces:**
- Consumes: renamed dir from Task 1.
- Produces: cards for **MockK, kotlinx-coroutines-test, Turbine, Kotest Property** that `SKILL.md` (Task 5) points into.

- [ ] **Step 1: Verify the tools are absent today**

Run: `grep -n "MockK\|Kotest\|Turbine\|coroutines-test" .claude/skills/jvm-testing-toolbox/references/tool-cards.md || echo "OK: absent"`
Expected: prints `OK: absent`.

- [ ] **Step 2: Append the Kotlin section**

At the end of `references/tool-cards.md`, add:
```markdown

## Kotlin & property testing (beyond the book)

- **MockK** — idiomatic Kotlin mocking. Note: reach for it over Mockito when you need
  `object` singletons (`mockkObject`), top-level/extension functions (`mockkStatic`),
  or *suspending* answers with real control (`coEvery { } coAnswers { }`) — **not**
  merely to mock final classes, which Mockito 5 does by default. `relaxed = true` /
  `@RelaxedMockK` avoids stubbing every call. In a mixed module the rule is **never
  two mockers on the same type**, not "one mocker per module".
- **kotlinx-coroutines-test** — test `suspend`/coroutine code. Note: `runTest { }`
  uses a virtual-time scheduler so `delay()` is skipped and tests stay
  deterministic. `StandardTestDispatcher` queues coroutines (advance with
  `advanceUntilIdle()`/`runCurrent()`); `UnconfinedTestDispatcher` runs them
  eagerly. Inject dispatchers into production code — hardcoded `Dispatchers.IO`
  can't be swapped for a `TestDispatcher`. **Not** a substitute for Awaitility:
  virtual time cannot wait on a real container or HTTP endpoint.
- **Turbine** — assert on `Flow` emissions. Note: `flow.test { awaitItem();
  awaitComplete() }` **fails if any emitted item goes unconsumed**, catching
  over-emission a plain `toList()` collect would hide. `awaitError()` for
  failures; `cancelAndIgnoreRemainingEvents()` for infinite flows.
- **Kotest Property** — property-based testing for Kotlin. Note: `checkAll` + `Arb`
  generators run **inside an ordinary Jupiter `@Test`** via `kotest-property` alone —
  no Kotest engine and no spec styles, so the module keeps a single test engine.
  (`kotest-assertions-core` is separable the same way if you want `shouldBe`.)
```
No Java-side property-testing card: jqwik is out of scope (second Platform engine,
maintenance mode, Anti-AI Usage Clause — see Global Constraints).

- [ ] **Step 3: Verify all four cards present**

Run: `grep -c "^- \*\*MockK\*\*\|^- \*\*kotlinx-coroutines-test\*\*\|^- \*\*Turbine\*\*\|^- \*\*Kotest Property\*\*" .claude/skills/jvm-testing-toolbox/references/tool-cards.md`
Expected: `4`. Also confirm `grep -c "Konsist\|jqwik" …` returns `0`.

- [ ] **Step 4: Fact-check the claims in these cards (Currency rule)**

The claims in Step 2 were verified on 2026-07-29 (see "Verified facts" above). Re-check
only if you altered the wording or added a claim. If you did, check it against the tool's
**current release notes or docs**, not memory. When current docs disagree, the docs win —
change the card and note it. Specifically re-check before shipping any change to:
Mockito's default mock-maker, `mockito-kotlin`'s `onBlocking`, or Kotest module
separability.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/tool-cards.md
git commit -s -m "Add Kotlin + property-testing tool cards

MockK, kotlinx-coroutines-test, Turbine, Kotest Property. Marked beyond
the book. Claims spot-checked against current docs per the Currency rule.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
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

## Kotlin pitfalls (beyond the book)

These tools and gotchas are **additions beyond Philip Riecks' (Java-framed) book**.

- **Mockito's Kotlin friction is smaller than its reputation.** Since **Mockito 5**
  the inline mock-maker is the default in `mockito-core`, so Kotlin's
  final-by-default classes mock with no extra dependency — the older
  `mockito-inline` / `mock-maker-inline` advice is stale. What still bites: `any()`
  can push `null` into a non-null Kotlin parameter and throw, which
  **mockito-kotlin** fixes (`whenever`, `mock<T>()`, nullable-safe matchers). It
  also stubs `suspend` functions via `onBlocking { }`.
- **Choose a mocker per type, not per module.** MockK earns its place for `object`s,
  extension/top-level functions, and suspending answers that need real control;
  Mockito + mockito-kotlin covers the rest. In a mixed source set both may sit on
  the classpath — an accepted cost, not an error. The actual mistake is **two
  mockers on the same type**, which produces confusing failures.
- **Coroutine tests must not use real time.** Use `runTest { }` (virtual time)
  with an injected `TestDispatcher` — not `runBlocking` + real `delay`, and never
  `Thread.sleep`. Production code must **take its dispatcher as a parameter**;
  hardcoded `Dispatchers.IO`/`Main` can't be replaced, so the test can't control
  scheduling. Choose `StandardTestDispatcher` (manual `advanceUntilIdle()`) vs
  `UnconfinedTestDispatcher` (eager) deliberately.
- **Don't use `runTest` to wait on real infrastructure.** Virtual time skips
  `delay()`; it cannot wait for a Testcontainers service or an HTTP endpoint —
  that is still **Awaitility**, in Kotlin exactly as in Java. Conversely, blocking
  inside `runTest` stalls the virtual clock. Coroutine scheduling and eventual
  consistency are different problems with different tools.
- **`Flow` tests silently pass without Turbine.** Collecting to a list and
  asserting size can miss extra/late emissions. **Turbine**'s `test { }` fails on
  any unconsumed item, so over-emission is caught.
- **PIT reports mislead on Kotlin.** The compiler emits `Intrinsics` null checks
  that PIT mutates, filling reports with `removed call to
  kotlin/jvm/internal/Intrinsics::… → SURVIVED` false positives. The option that
  suppresses them also stops mutating any statement containing a null check —
  including real business logic. Read Kotlin mutation scores with that in mind.
- **Data classes change what you assert.** `equals`/`hashCode` are generated, so
  assert whole-object equality (`shouldBe`, AssertJ `isEqualTo`) instead of
  field-by-field — but `copy()` is shallow, so deep structures still need care.
```

- [ ] **Step 3: Verify present, attributed, and free of the stale Mockito claim**

Run:
```bash
grep -n "Kotlin pitfalls (beyond the book)\|Choose a mocker per type\|PIT reports mislead on Kotlin\|wait on real infrastructure" .claude/skills/jvm-testing-toolbox/references/pitfalls.md && \
grep -n "mock-maker-inline\|can't mock them without" .claude/skills/jvm-testing-toolbox/references/pitfalls.md || echo "OK: no stale inline-mock-maker claim"
```
Expected: four matching lines from the first grep; the second prints the `OK:` line.

- [ ] **Step 4: Fact-check the claims in this section (Currency rule)**

Verified on 2026-07-29 (see "Verified facts" above). Re-check against current release
notes if you reworded anything, especially the Mockito 5 default mock-maker claim, the
`onBlocking` suspend-stubbing claim, and PIT's Kotlin `Intrinsics` behavior. Docs win
over this file.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/pitfalls.md
git commit -s -m "Add Kotlin pitfalls (mocker choice, coroutine time, Flow, PIT on Kotlin)

Marked beyond the book. Corrects the stale 'Mockito needs the inline
mock-maker for Kotlin final classes' advice — default since Mockito 5 —
and separates coroutine virtual time from Awaitility's wall-clock waiting.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
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
because real JVM projects mix Java and Kotlin, frequently in one source set.

Load this once routing has landed on a Kotlin-specific tool, **or when Java and
Kotlin tests in the same module interfere with each other** (last section). For the
quick decision, use the "Kotlin on the JVM" table in `SKILL.md`.

## MockK vs Mockito (+ mockito-kotlin)

- **Mockito is more capable on Kotlin than its reputation suggests.** Since
  **Mockito 5** the inline mock-maker is the default in `mockito-core`, so
  final-by-default Kotlin classes mock with **no extra dependency and no
  `mock-maker-inline` resource file**. `mockito-kotlin` adds `whenever`,
  `mock<T>()`, `argumentCaptor`, nullable-safe matchers (its `any()` won't push
  `null` into a non-null parameter), and `onBlocking { }` for stubbing `suspend`
  functions.
- **MockK earns its place** where Mockito genuinely can't be idiomatic: `object`
  singletons (`mockkObject`), top-level and extension functions (`mockkStatic`),
  and *suspending* answers needing real control (`coEvery { } coAnswers { … }`) —
  `onBlocking` handles simple returns but gets awkward with delays, indefinite
  suspension, and value-class boxing. `relaxed = true` / `@RelaxedMockK` returns
  sensible defaults; use a strict mock when unstubbed calls should fail.
- **The rule is one mocker per *type*, not per module.** Two mockers on the same
  type causes confusing failures. Two mockers in the same *module* — Mockito in the
  Java tests, MockK in the Kotlin ones — is a normal state for a mixed source set.
  It costs a second mental model; pay that deliberately rather than by accident.
- **When to stay on Mockito:** a mostly-Java module where a few tests happen to be
  Kotlin, or heavy Spring `@MockitoBean` integration. **Reach for MockK** in
  Kotlin-first or coroutine-heavy code.

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
- **Virtual time is not a waiting mechanism.** `runTest` can skip a `delay()` your
  own code issues; it cannot wait for a Testcontainers service, an HTTP endpoint, or
  a message to land on a broker. Those stay **Awaitility**, in Kotlin as in Java.
  Blocking inside `runTest` to bridge the gap stalls the virtual clock — the test
  hangs or silently takes real time.

## Flow testing: Turbine

- `flow.test { … }` collects the flow inside a scope and **requires every emission
  to be consumed** — `awaitItem()`, `awaitComplete()`, `awaitError()`. If the flow
  emits more than the test consumes, the block fails; a plain `toList()` collect
  would silently pass.
- For infinite/hot flows, end with `cancelAndIgnoreRemainingEvents()`.
- Combine with virtual time (`runTest`) when the flow uses `delay`/`debounce`.

## Property testing: Kotest Property

- **`kotest-property` is a plain library, and that is the whole point.**
  `checkAll { a, b -> … }` runs inside an ordinary Jupiter `@Test` — no Kotest
  engine, no spec styles — so the module keeps a single test engine.
- It shrinks a failure to a minimal counterexample, which is what makes property
  testing worth more than hand-rolled random input.
- **No Java-side equivalent is recommended.** jqwik is the obvious candidate and is
  deliberately excluded: it registers its own Platform engine, is in pure
  maintenance mode, and carries an Anti-AI Usage Clause from v1.10. If Java-side
  invariants genuinely need property testing, that is a considered exception to make
  explicitly — not a default this skill routes you into.
- `kotest-assertions-core` is separable the same way (`shouldBe`, `shouldThrow`) if
  you want Kotlin-idiomatic assertions without adopting the Kotest engine.

## Mixed source set: Java and Kotlin in one module

These bite only when both languages compile into the same source set — the case this
skill treats as primary.

- **`@BeforeAll` / `@AfterAll` / `@MethodSource` need `@JvmStatic`.** JUnit requires
  them to be static; Kotlin has no `static`, so they belong in a `companion object`
  marked `@JvmStatic`. The alternative is annotating the class
  `@TestInstance(Lifecycle.PER_CLASS)`, which removes the static requirement — usually
  cleaner in Kotlin, but it shares one instance across every test in the class, so
  mutable state now leaks between them.
- **Platform types quietly weaken null assertions.** A Java method returning `String`
  appears to Kotlin as `String!` — nullability unknown — so the compiler neither forces
  a check nor flags a redundant one. Assertions against Java-returned values can look
  null-safe while proving nothing. Annotate the Java side (JSpecify / `@Nullable`) or
  assert explicitly.
- **`internal` and test friend-paths.** Kotlin `internal` compiles to `public` with a
  mangled name, so same-module Java test code can reach it. Kotlin test code can too —
  but only because the build marks the test compilation a *friend* of main. The Gradle
  Kotlin plugin does this for the standard `test` source set; a custom source set
  won't get it automatically, and `internal` members will look mysteriously
  inaccessible.
- **JUnit 6 runs `suspend` test functions natively** (Java 17+ / Kotlin 2.2+), so the
  test method needs no `runBlocking` wrapper. You still want `runTest` for virtual time.
- **Backtick test names are JVM-legal but not portable.** Fine on the JVM; some tooling
  (and Android) rejects the characters. `@DisplayName` is the portable equivalent and
  reads the same from both languages.
- **Mutation scores aren't comparable across the two languages** in one module — see
  the PIT bullet in `pitfalls.md`.
```

- [ ] **Step 3: Verify the file exists with all five headings**

Run: `grep -n "^## " .claude/skills/jvm-testing-toolbox/references/kotlin.md`
Expected: `5` headings — MockK vs Mockito, Coroutine testing, Flow testing, Property
testing, Mixed source set. Confirm no Konsist heading.

- [ ] **Step 4: Fact-check the claims in this file (Currency rule)**

Verified on 2026-07-29 (see "Verified facts" above). If you reworded anything, re-check
against current docs — particularly the Mockito 5 mock-maker default, `onBlocking`,
JUnit 6 `suspend` support, and Kotlin test friend-paths.
Docs win over this file; if one disagrees, change the file and say so.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/references/kotlin.md
git commit -s -m "Add references/kotlin.md (Kotlin tool depth + mixed source-set interop)

MockK vs Mockito, coroutine virtual time, Flow, property testing, and the
Java/Kotlin interop traps that only appear in a shared source set:
@JvmStatic lifecycle methods, platform types, internal friend-paths.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
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
(JUnit 5/6, Mockito, AssertJ, MockK) is already known.
```
(The line currently reads `(JUnit 5/6, Mockito, AssertJ)` — add `, MockK`.)
This keeps the "router, not a tutorial" identity intact: basic usage of the named
tools is assumed, and `references/kotlin.md` carries **tie-breakers and interop
traps**, not usage walkthroughs.

- [ ] **Step 3: Add the "beyond the book" note to the source paragraph**

After the sentence ending `github.com/rieckpil/java-testing-ecosystem`.` add a new sentence in the same paragraph:
```
 Kotlin-native tools (MockK, kotlinx-coroutines-test, Turbine, Kotest Property)
are additions **beyond the book**, included because real JVM projects mix Java
and Kotlin — often in one source set.
```

- [ ] **Step 4: Add the language-agnostic framing to "How to use this skill"**

After the numbered list in `## How to use this skill` (after the "Only pull deeper detail…" item), add:
```markdown

**Java or Kotlin?** These tables apply to both. Where Kotlin has an idiomatic
swap, the row's note names it (**Kotlin:** …); Kotlin-only concerns (coroutines,
`Flow`) are in the **Kotlin on the JVM** section below. For Kotlin depth and the
Java/Kotlin interop traps, open `references/kotlin.md`.

**One engine.** In a mixed Java+Kotlin module, run **JUnit Jupiter as the only
test engine** — one runner, one report, one CI config. Libraries may differ per
file; engines should not. That is why Kotest appears here as an assertion and
property-testing *library* rather than a framework, and why no tool requiring a
second engine appears here at all.
```

- [ ] **Step 5: Inline swap — Mockito row (Mocking & stubbing table)**

In the Mockito row, append to the tie-breaker/note cell (after "…final classes and statics mock with no extra dependency."):
```
 **Kotlin:** that also covers Kotlin's final-by-default classes, and `mockito-kotlin` adds null-safe matchers plus `onBlocking` for `suspend` functions. Reach for **MockK** for `object`s, extension/top-level fns, or suspending answers needing real control. Never two mockers on the same type. **Beyond the book.**
```

- [ ] **Step 6: Inline swap — AssertJ row (Assertion libraries table)**

In the AssertJ row, append to the note cell (after "…custom `AbstractAssert` for domain types."):
```
 **Kotlin:** `kotest-assertions-core` (`x shouldBe y`) is an idiomatic alternative that needs no Kotest engine; AssertJ itself works unchanged from Kotlin.
```

- [ ] **Step 7: New row — property-based testing (Architecture & test quality table)**

Property testing has no row today. Add one immediately after the Instancio row:
```markdown
| Generate inputs and assert an invariant holds (Kotlin) | **Kotest Property** | `checkAll` + `Arb` via `kotest-property` alone — runs inside a Jupiter `@Test`, no Kotest engine, one engine preserved. Shrinks failures to a minimal counterexample. No Java-side entry: jqwik would add a second Platform engine, is in maintenance mode, and carries an Anti-AI Usage Clause. **Beyond the book.** |
```

Note: **no ArchUnit swap.** ArchUnit reads bytecode and already runs against Kotlin; Konsist is out of scope per Global Constraints.

- [ ] **Step 8: Add the "Kotlin on the JVM" section**

Immediately before `## Cross-cutting reminders`, insert:
```markdown
### Kotlin on the JVM

Most tables above apply to Kotlin unchanged. These are the Kotlin-**specific**
choices — a swap for a shared concern, plus axes with no Java equivalent. All are
**beyond Riecks' (Java-framed) book**; depth and the mixed-source-set interop
traps are in `references/kotlin.md`.

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock a Kotlin `object`, extension fn, or suspending answer | **MockK** | `mockkObject`, `mockkStatic`, `coEvery { } coAnswers { }`. For ordinary classes Mockito 5 + `mockito-kotlin` is fine — final classes mock by default, `onBlocking` stubs `suspend` fns. Never two mockers on the same type. |
| Test `suspend` functions / coroutine scheduling | **kotlinx-coroutines-test** | `runTest { }` drives virtual time; advance with `advanceUntilIdle()` / `runCurrent()`. Inject dispatchers — don't hardcode `Dispatchers.IO`. **Not** for waiting on real infrastructure — that stays Awaitility. |
| Assert on values a `Flow` emits | **Turbine** | `flow.test { awaitItem(); awaitComplete() }` — fails on unconsumed items, unlike a plain `toList()` collect. Pairs with any assertion lib. |
| Fix Java/Kotlin interop in one source set | `references/kotlin.md` | `@JvmStatic` for `@BeforeAll`/`@MethodSource`, platform types weakening null assertions, `internal` friend-paths, PIT noise on Kotlin null checks. |

```

- [ ] **Step 9: Add Kotlin cross-cutting reminders**

In `## Cross-cutting reminders`, add three bullets (after the "Awaitility over `Thread.sleep`" bullet):
```markdown
- **One engine in a mixed module** — JUnit Jupiter runs both languages. Bring Kotest
  in as a library (assertions, property testing), not as a second engine.
- **Kotlin mocking: choose per type, not per module.** Mockito 5 + `mockito-kotlin`
  covers most Kotlin (final classes mock by default; `onBlocking` stubs `suspend`
  fns); **MockK** for `object`s, extension fns, and suspending answers. Never two
  mockers on the same type.
- **Kotlin coroutines: `runTest` + an injected `TestDispatcher`**, never real delays
  or `Thread.sleep`; **Turbine** for `Flow`. Waiting on real infrastructure is still
  **Awaitility** — virtual time cannot wait on a container.
```

- [ ] **Step 10: Verify Kotlin routing content is present, and Konsist is absent**

Run:
```bash
grep -n "Kotlin on the JVM\|Java or Kotlin?\|One engine\|MockK\|Kotest Property\|kotest-assertions-core\|kotlinx-coroutines-test\|Turbine\|references/kotlin.md" .claude/skills/jvm-testing-toolbox/SKILL.md && \
grep -n "Konsist" .claude/skills/jvm-testing-toolbox/SKILL.md || echo "OK: no Konsist"
```
Expected: matches for the section heading, both framing lines, every tool name, and the `references/kotlin.md` link; the second grep prints the `OK:` line.

- [ ] **Step 11: Verify table integrity (no broken Markdown rows)**

Read the "Test frameworks", "Mocking & stubbing", "Assertion libraries", "Architecture & test quality", and new "Kotlin on the JVM" tables. Confirm every row has the same pipe-column count as its header (3 columns). Fix any row that doesn't.

- [ ] **Step 12: Commit**

```bash
git add .claude/skills/jvm-testing-toolbox/SKILL.md
git commit -s -m "Make SKILL.md router Kotlin-aware (one-engine rule, swaps, Kotlin section)

Language-agnostic framing plus an explicit one-engine rule; corrected
Mockito/MockK guidance; a new Kotlin property-testing row (Kotest
Property, engine-free); a 'Kotlin on the JVM' table for coroutine/Flow
testing and interop.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
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
    └── kotlin.md            # Kotlin depth + Java/Kotlin interop in one source set
```

- [ ] **Step 5: Add coverage rows for the new tools**

After the "Architecture & quality" row, add two rows. Use **plain category cells** —
every other row is a bare category name, and the "beyond the book" caveat belongs in
prose below the table (the convention commit `63c40cf` established when it added
JUnit 6):
```markdown
| Kotlin | MockK, kotlinx-coroutines-test, Turbine, Kotest Property |
```
Then, after the coverage table's trailing paragraph about JUnit 6, add:
```markdown

The Kotlin tools (MockK, kotlinx-coroutines-test, Turbine, Kotest Property) are
**additions beyond the book's Java tools**, because real JVM projects frequently mix
Java and Kotlin — often in one source set.
```

- [ ] **Step 6: Correct the `## Credit` section**

The Credit section was already corrected once (the curation commit) and now reads
"The Java tool selection … distilled from that book — **curated rather than
mirrored**". It still needs the Kotlin additions named, or the section implies the
book covers them. Append to that sentence:
```markdown
The Kotlin coverage (MockK, kotlinx-coroutines-test, Turbine, Kotest Property) and
the mixed Java/Kotlin interop notes are **additions beyond the book** — not Philip's
work, and not to be attributed to him.
```
Leave the rest of the Credit section (the book blockquote, the links, the
"no reproduction of the book's prose" paragraph) untouched.

- [ ] **Step 7: Update the Usage path**

Change `Drop the `.claude/skills/java-testing-toolbox/` directory` to
`Drop the `.claude/skills/jvm-testing-toolbox/` directory`.

- [ ] **Step 8: Verify README updated, credit corrected, no stale slug**

Run:
```bash
grep -n "jvm-testing-toolbox\|Renamed from\|| Kotlin |\|| Property-based |\|kotlin.md" README.md && \
grep -n "additions beyond the" README.md && \
grep -n "All 30 tools" README.md || echo "OK: stale credit claim removed" && \
grep -n "java-testing-toolbox" README.md
```
Expected: new-slug and coverage lines present; the corrected credit sentence present;
`OK: stale credit claim removed` printed; the only `java-testing-toolbox` hit is inside
the "Renamed from" note.

- [ ] **Step 9: Commit**

```bash
git add README.md
git commit -s -m "Update README for jvm-testing-toolbox rename + Kotlin coverage

Corrects the Credit section, which claimed every tool and pitfall came
from Philip Riecks' book — no longer true once Kotlin and property-testing
coverage is added. Attribution for the Java core is unchanged.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
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

- [ ] **Step 4: Scope sweep — Konsist and Kotest-as-framework are absent**

Run:
```bash
grep -rn "Konsist" .claude/skills/ README.md || echo "OK: no Konsist"
grep -rn "StringSpec\|BehaviorSpec\|FunSpec\|spec styles" .claude/skills/ || echo "OK: no Kotest spec styles"
```
Expected: both print their `OK:` line. Konsist is out of scope; Kotest enters as a library only (assertions + property testing) under the one-engine rule.

- [ ] **Step 5: Currency check — every new version-sensitive claim was actually verified**

Confirm each content task's fact-check step was performed rather than skipped. The `Last verified: 2026-07` stamp now covers Kotlin and property-testing claims, so it must not be a promise nobody kept. Spot-check at minimum: Mockito's default mock-maker, `mockito-kotlin`'s `onBlocking`, Kotest module separability, JUnit 6 `suspend` support, and PIT's Kotlin `Intrinsics` behavior. If a current doc disagrees with a shipped line, change the line and say so.

- [ ] **Step 6: Attribution check**

Run: `grep -n "All 30 tools" README.md || echo "OK: credit corrected"`
Expected: prints the `OK:` line. Then confirm **every** place the new tools appear signals "beyond the book" — SKILL.md's source paragraph, its Kotlin section intro, the annotated rows, the `tool-cards.md` heading, the `pitfalls.md` heading, `kotlin.md`'s intro, and README's prose *and* Credit section. Nothing may imply the book covers Kotlin or property testing.

- [ ] **Step 7: Routing sanity (manual read)**

Read `SKILL.md` top-to-bottom once. Confirm: (a) a Java-only reader sees no Kotlin noise except the annotated rows + the Kotlin section; (b) a Kotlin prompt ("mock a Kotlin `object`", "test a `suspend` function", "test a `Flow`") has an obvious landing row; (c) a mixed-source-set prompt ("`@BeforeAll` doesn't run in my Kotlin test") routes to `references/kotlin.md`; (d) every tool named in a table has a matching card in `tool-cards.md`.

- [ ] **Step 8: Push the branch (updates PR #1)**

```bash
git push
```
Then print the PR URL as plain text on its own line:
`https://github.com/adityamparikh/java-testing-skill/pull/1`

## Self-Review

**Spec coverage** (checked against `docs/superpowers/specs/2026-07-23-jvm-testing-kotlin-overlay-design.md`):
- Frame shared tables language-agnostic → Task 5 Step 4. ✅
- One-engine rule stated explicitly → Task 5 Step 4 (framing) + Step 9 (reminder). ✅
- Inline swaps on Mockito + AssertJ; **no ArchUnit swap** (Konsist out of scope) → Task 5 Steps 5–6. ✅
- Property-testing row (Kotest Property, Kotlin-side only; jqwik excluded) → Task 5 Step 7. ✅
- New "Kotlin on the JVM" section (MockK, coroutines, Flow, interop pointer) → Task 5 Step 8. ✅
- New `references/kotlin.md`, incl. the mixed-source-set interop half → Task 4. ✅
- Rename dir + name + description + old-name note → Task 1 + Task 6 Step 2. ✅
- tool-cards additions (MockK, coroutines-test, Turbine, Kotest Property) → Task 2. ✅
- pitfalls additions (incl. PIT-on-Kotlin, mocker choice, runTest vs Awaitility) → Task 3. ✅
- README name + coverage + **Credit correction** → Task 6 Steps 1–6. ✅
- Decisions locked: coroutine depth (route + gotcha in tables, nuance in kotlin.md) → Tasks 4/5; **"beyond the book" framing → Tasks 2, 3, 4, 5, 6** (Task 3 was previously missing from this list and from its own section heading — fixed). ✅
- Currency: a fact-check step now ends every content task (2, 3, 4) with a sweep in Task 7 Step 5; verified facts recorded up front so they aren't re-derived. ✅
- Out-of-scope respected: no swap column, no per-language split, no Konsist, no Kotest spec styles, no Spring Kotlin wiring, no Android, no build-tool guidance. ✅

**Placeholder scan:** No TBD/TODO; every edit shows literal content and an anchor. ✅

**Correctness scan:** The stale "Mockito needs the inline mock-maker for Kotlin final classes" claim (Mockito 4-era; default since Mockito 5) is removed from the spec, Task 3, Task 4, and Task 5, and replaced with the verified position. "Mockito can't stub `suspend` functions" is likewise avoided — `mockito-kotlin`'s `onBlocking` can; MockK's advantage is ergonomics and advanced cases. ✅

**Type/name consistency:** Slug `jvm-testing-toolbox` used identically in Tasks 1, 6, 7; section heading `Kotlin on the JVM` produced in Task 5 Step 8 and referenced in Task 5 Step 4; file `references/kotlin.md` created in Task 4 and linked in Task 5 Steps 4/8 + Task 6 Step 4. Commit trailer is `Claude Opus 5 (1M context)` in every task. ✅
