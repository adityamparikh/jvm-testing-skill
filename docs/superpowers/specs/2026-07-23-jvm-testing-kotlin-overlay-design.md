# Design: Add Kotlin overlay to the testing-toolbox skill (mixed Java+Kotlin)

**Date:** 2026-07-23
**Revised:** 2026-07-29 — scope narrowed (Konsist dropped, property testing added),
one-engine rule made explicit, mocking guidance corrected against current Mockito,
mixed-source-set interop content added.
**Status:** Approved (design), pending spec review → implementation plan
**Skill:** `java-testing-toolbox` → renamed `jvm-testing-toolbox`

## Problem

The skill is a router that maps a testing problem to the right JVM tool. It is
currently framed as Java-only (name `java-testing-toolbox`, Java-only triggers),
yet real JVM projects are frequently **mixed Java + Kotlin** — Java production
with Kotlin tests, gradual Kotlin migration, or a Kotlin app calling Java
libraries. The primary case is stronger than "same repo": **both languages in the
same module and the same source set**, sharing one classpath, one compile step,
and one JUnit Platform launcher. That sharing is what makes tool choices collide.

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
- Idiomatic Kotlin **swap** on an existing concern: mocking (Mockito → MockK,
  conditionally — see "Decisions locked").
- Kotlin-**only** concern with no Java-equivalent row: coroutine testing
  (`kotlinx-coroutines-test`), `Flow` testing (Turbine).
- **Different problem, not a swap:** asynchrony. Awaitility polls wall-clock for
  an eventual state; `runTest` advances a virtual clock inside a coroutine. These
  are not substitutes and must not be presented as a language swap — an agent
  that treats `runTest` as "Kotlin Awaitility" writes tests that hang.
- **Gap in both languages:** property-based testing has no row today.

Sparse divergence → inline annotations on the rows that differ, plus a small
dedicated section for the Kotlin-only axes. Not a swap column across all tables
(most cells would say "same" → noise), and not a walled-off Kotlin section for
the swaps (a mixed-repo dev needs the swap at the decision point).

## Governing rule: one engine

**JUnit Jupiter is the sole test engine for the module.** One runner, one report,
one CI config. Libraries may differ per file; engines may not. This is what keeps
a shared source set coherent, and it decides several rows below:

- Kotest is included **only** as a property-testing and assertion library callable
  from a Jupiter `@Test`, never for its spec styles (which need Kotest's engine).
- **No Java-side property-testing entry.** jqwik is the obvious candidate and is
  excluded: it registers its own Platform engine (breaking the rule), is in pure
  maintenance mode, and ships an **Anti-AI Usage Clause** from v1.10 — which
  disqualifies it from a skill whose sole consumer is an AI coding agent.

## Design (hybrid)

### 1. Frame shared tables as language-agnostic
Add one line under "How to use this skill":
> These tables apply to Java and Kotlin alike. Where Kotlin has an idiomatic
> swap, the row names it; Kotlin-only concerns are in the "Kotlin on the JVM"
> section below.

### 2. Inline Kotlin swap on the rows that actually differ
- **Mocking / Mockito row** → add: Kotlin: **MockK** for `object`s, extension /
  top-level functions, and complex suspending answers. Mockito 5's inline
  mock-maker already handles Kotlin's final-by-default classes with no extra
  dependency, and `mockito-kotlin`'s `onBlocking` stubs `suspend` functions — so
  staying on Mockito is viable.
- **Frameworks + Assertions** → note **Kotest assertions** (`shouldBe`) as an
  idiomatic Kotlin option addable standalone (`kotest-assertions-core`) without
  adopting the Kotest engine; JUnit 6 + AssertJ work fine in Kotlin.

### 3. New "Kotlin on the JVM" section (Kotlin-only concerns)

| I need to… | Reach for | Note |
|---|---|---|
| Test `suspend` functions / coroutine logic | **`kotlinx-coroutines-test`** | `runTest`, virtual-time `TestDispatcher`; `advanceUntilIdle` / `runCurrent`. Inject dispatchers — don't hardcode `Dispatchers.IO`. Not a replacement for Awaitility. |
| Assert on values emitted by a `Flow` | **Turbine** | `flow.test { awaitItem(); awaitComplete() }`. Pairs with any assertion lib. |
| Mock `object`s / extension fns / suspending answers | **MockK** | Cross-linked from the Mocking table. |
| Fix Java/Kotlin interop in one source set | `references/kotlin.md` | `@JvmStatic` lifecycle methods, platform types, `internal` friend-paths, PIT noise. |

### 4. Property-based testing (new row, both languages)

| I need to… | Reach for | Note |
|---|---|---|
| Generate inputs and assert an invariant holds (Kotlin) | **Kotest Property** | `checkAll` + `Arb` run inside an ordinary Jupiter `@Test` via `kotest-property` alone — no Kotest engine, no spec styles, one engine preserved. Shrinks failures to a minimal counterexample. |

### 5. New `references/kotlin.md` for depth
Two halves:
- **Kotlin tool depth:** MockK vs Mockito + `mockito-kotlin` trade-offs;
  `StandardTestDispatcher` vs `UnconfinedTestDispatcher` (+ `advanceUntilIdle` vs
  `runCurrent`); Turbine usage notes; dispatcher-injection rationale.
- **Mixed source-set interop** (the half that earns "same source set"):
  `@JvmStatic` for `@BeforeAll`/`@MethodSource`; platform types (`String!`)
  silently defeating null assertions on Java-returned values; `internal`
  visibility and test friend-paths; PIT mutating Kotlin's generated `Intrinsics`
  null checks; JUnit 6 native `suspend` test functions.

### 6. Rename + retrigger
- Rename directory + `name` → `jvm-testing-toolbox`.
- Broaden `description` with Kotlin triggers: MockK, Kotest, coroutines,
  `Flow`/Turbine, "mock a Kotlin `object`", "test suspend functions",
  "mixed Java/Kotlin source set", property-based testing.
- Note the old name (`java-testing-toolbox`) in `README.md` so existing
  references/searches still resolve.

## Decisions locked
- **One engine (Jupiter).** Libraries may differ per file; engines may not. Kotest
  enters as a library only, and no tool requiring a second engine is recommended.
- **Mocking in a shared source set.** The rule is **never two mockers on the same
  type** — not "one mocker per module". Mockito 5 + `mockito-kotlin` covers most
  Kotlin needs (final classes work by default; `onBlocking` stubs `suspend`
  functions). Reach for MockK for `object`s, extension/top-level functions, or
  suspending answers that need real control. In a mixed source set, both mockers
  on the classpath is an accepted cost when justified, not an error.
- **Coroutine-test depth:** route + one high-signal gotcha per tool in the
  table; full nuance in `references/kotlin.md` (consistent with the rest of the
  skill).
- **Source fidelity:** Riecks' *Java Testing Toolbox* is Java-framed; mark
  Kotlin and property-testing tools as "beyond the book" additions rather than
  implying the book covers them. This includes updating README's Credit section,
  which currently claims all tools and pitfalls are distilled from the book.
- **Currency:** new version-sensitive claims must be spot-checked against current
  release notes before the `Last verified` stamp is applied to them.

## Out of scope (YAGNI)
- No swap column across all tables.
- No per-language skill split.
- **No Konsist.** ArchUnit reads bytecode and already runs on Kotlin; Konsist's
  extra reach (top-level/extension functions) doesn't justify a second
  architecture tool in a skill whose value is fewer, better-defended choices.
- **No Kotest spec styles** — excluded by the one-engine rule.
- **No jqwik.** Second Platform engine, pure maintenance mode, and an Anti-AI Usage
  Clause since v1.10 that makes it inappropriate to route an AI agent toward.
  Property testing is offered on the Kotlin side only.
- **No Spring Boot Kotlin test wiring** (`@MockkBean`, all-open/no-arg plugins).
  The `spring-boot` skill owns Spring specifics; duplicating them here creates
  two places to go stale.
- No Android / Robolectric.
- No Kotlin build-tool / Gradle-DSL guidance (this is a test-tool router, not a
  build skill).
- No exhaustive Kotlin assertion-library survey (Strikt/Kluent get at most a
  one-line mention; Kotest assertions are the named option).

## Files touched
- `.claude/skills/java-testing-toolbox/` → renamed to
  `.claude/skills/jvm-testing-toolbox/`
- `jvm-testing-toolbox/SKILL.md` — frontmatter (name/description), language-
  agnostic framing, one-engine rule, inline swaps, new "Kotlin on the JVM"
  section, property-testing row, cross-cutting reminders touch-up.
- `jvm-testing-toolbox/references/kotlin.md` — new (tool depth + interop).
- `jvm-testing-toolbox/references/tool-cards.md` — add cards for MockK,
  `kotlinx-coroutines-test`, Turbine, Kotest Property.
- `jvm-testing-toolbox/references/pitfalls.md` — add Kotlin pitfalls (dispatcher
  hardcoding, `Flow` over-emission, PIT on Kotlin null checks, mocker mixing).
- `README.md` — new name + old-name note + **Credit section corrected** so it no
  longer claims every tool and pitfall comes from the book.

## Success criteria
- A Kotlin-only question ("how do I test a `suspend` function?", "mock a Kotlin
  `object`") routes to this skill via its description.
- Shared tables still read cleanly for a Java-only user (no per-row Kotlin
  noise except the annotated rows + the Kotlin section).
- A mixed-source-set dev finds: the mocking guidance at the decision point,
  coroutine/`Flow` testing in one obvious place, and the interop traps
  (`@JvmStatic`, platform types, PIT noise) in `references/kotlin.md`.
- Asynchrony reads as three distinct problems, not one with a Kotlin variant.
- Every new version-sensitive claim has been spot-checked against current docs,
  per the Currency rule.
- No attribution in README or the skill implies the book covers Kotlin tooling.
- Build/tests unaffected (skill is docs-only; no code build here — verify the
  repo has no build to run).
