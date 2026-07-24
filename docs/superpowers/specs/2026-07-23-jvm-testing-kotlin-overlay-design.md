# Design: Add Kotlin overlay to the testing-toolbox skill (mixed Java+Kotlin)

**Date:** 2026-07-23
**Status:** Approved (design), pending spec review → implementation plan
**Skill:** `java-testing-toolbox` → renamed `jvm-testing-toolbox`

## Problem

The skill is a router that maps a testing problem to the right JVM tool. It is
currently framed as Java-only (name `java-testing-toolbox`, Java-only triggers),
yet real JVM projects are frequently **mixed Java + Kotlin** — Java production
with Kotlin tests, gradual Kotlin migration, or a Kotlin app calling Java
libraries. A developer may toggle between writing a Java test and a Kotlin test
in the same repo.

Two skills (one per language) is the wrong call: the routing decision is ~80%
identical across languages, and per-language skills would produce heavily
overlapping trigger descriptions that degrade selection precision in mixed
repos. The decision is to keep **one JVM-scoped skill** and treat Kotlin as an
overlay on the shared router.

## Key observation

The Java/Kotlin divergence is **sparse and localized**, not spread evenly:

- Shared (used identically): JUnit, AssertJ, Testcontainers, WireMock,
  MockWebServer, REST Assured, Awaitility (wall-clock), Gatling, JMH, JsonPath,
  JSONAssert, XMLUnit, Selenide, Pact, Instancio, PIT, ArchUnit (rules run on
  both), etc.
- Idiomatic Kotlin **swap** on an existing concern: mocking (Mockito → MockK),
  architecture (ArchUnit → Konsist), framework/assertions (JUnit+AssertJ work;
  Kotest is the idiomatic option).
- Kotlin-**only** concern with no Java-equivalent row: coroutine testing
  (`kotlinx-coroutines-test`), `Flow` testing (Turbine).

Sparse divergence → inline annotations on the ~4 rows that differ, plus a small
dedicated section for the Kotlin-only axes. Not a swap column across all tables
(most cells would say "same" → noise), and not a walled-off Kotlin section for
the swaps (a mixed-repo dev needs the swap at the decision point).

## Design (hybrid)

### 1. Frame shared tables as language-agnostic
Add one line under "How to use this skill":
> These tables apply to Java and Kotlin alike. Where Kotlin has an idiomatic
> swap, the row names it; Kotlin-only concerns are in the "Kotlin on the JVM"
> section below.

### 2. Inline Kotlin swap on the rows that actually differ
- **Mocking / Mockito row** → add: Kotlin: prefer **MockK** (final-by-default
  classes, coroutines, objects, extension functions native); Mockito needs
  `mockito-kotlin` + inline mock-maker.
- **Architecture / ArchUnit row** → add: Kotlin: **Konsist** understands Kotlin
  declarations natively.
- **Frameworks + Assertions** → note **Kotest** as the idiomatic Kotlin option
  (spec styles, property testing, `shouldBe` matchers); JUnit 6 + AssertJ work
  fine in Kotlin too. (JUnit 6 needs Kotlin 2.2+ note already exists.)

### 3. New "Kotlin on the JVM" section (Kotlin-only concerns)

| I need to… | Reach for | Note |
|---|---|---|
| Test `suspend` functions / coroutine logic | **`kotlinx-coroutines-test`** | `runTest`, virtual-time `TestDispatcher`; `advanceUntilIdle` / `runCurrent`. Inject dispatchers — don't hardcode `Dispatchers.IO`. |
| Assert on values emitted by a `Flow` | **Turbine** | `flow.test { awaitItem(); awaitComplete() }`. Pairs with any assertion lib. |
| Mock Kotlin-idiomatically | **MockK** | Cross-linked from the Mocking table. |
| Kotlin-native architecture rules | **Konsist** | Cross-linked from the Architecture table. |

### 4. New `references/kotlin.md` for depth
MockK vs Mockito trade-offs and the final-class / `mockito-inline` gotcha;
`StandardTestDispatcher` vs `UnconfinedTestDispatcher` (+ `advanceUntilIdle` vs
`runCurrent`); Kotest spec styles and when it earns its place vs JUnit; Turbine
usage notes; dispatcher-injection rationale.

### 5. Rename + retrigger
- Rename directory + `name` → `jvm-testing-toolbox`.
- Broaden `description` with Kotlin triggers: MockK, Kotest, coroutines,
  `Flow`/Turbine, Konsist, "mock a final Kotlin class", "test suspend functions".
- Note the old name (`java-testing-toolbox`) in `README.md` so existing
  references/searches still resolve.

## Decisions locked
- **Coroutine-test depth:** route + one high-signal gotcha per tool in the
  table; full nuance in `references/kotlin.md` (consistent with the rest of the
  skill).
- **Source fidelity:** Riecks' *Java Testing Toolbox* is Java-framed; mark
  Kotlin tools as "beyond the book" additions rather than implying the book
  covers them.

## Out of scope (YAGNI)
- No swap column across all tables.
- No per-language skill split.
- No Kotlin build-tool / Gradle-DSL guidance (this is a test-tool router, not a
  build skill).
- No exhaustive Kotlin assertion-library survey (Strikt/Kluent get at most a
  one-line mention; Kotest is the named default).

## Files touched
- `.claude/skills/java-testing-toolbox/` → renamed to
  `.claude/skills/jvm-testing-toolbox/`
- `jvm-testing-toolbox/SKILL.md` — frontmatter (name/description), language-
  agnostic framing, inline swaps on ~4 rows, new "Kotlin on the JVM" section,
  cross-cutting reminders touch-up.
- `jvm-testing-toolbox/references/kotlin.md` — new.
- `jvm-testing-toolbox/references/tool-cards.md` — add cards for MockK, Kotest,
  `kotlinx-coroutines-test`, Turbine, Konsist.
- `jvm-testing-toolbox/references/pitfalls.md` — add Kotlin pitfalls (final
  classes + Mockito, dispatcher hardcoding, mixing MockK + Mockito).
- `README.md` — reflect new name + old-name note.

## Success criteria
- A Kotlin-only question ("how do I test a `suspend` function?", "mock a final
  Kotlin class") routes to this skill via its description.
- Shared tables still read cleanly for a Java-only user (no per-row Kotlin
  noise except the ~4 rows that differ).
- A mixed-repo dev sees the Kotlin swap at the decision point for mocking and
  architecture, and finds coroutine/`Flow` testing in one obvious place.
- Build/tests unaffected (skill is docs-only; no code build here — verify the
  repo has no build to run).
