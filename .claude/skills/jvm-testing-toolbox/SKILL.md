---
name: jvm-testing-toolbox
description: >-
  Use when choosing which JVM testing tool to reach for on a specific challenge
  in a Java and/or Kotlin project — including when both languages share one
  module and source set. Covers picking a test framework, assertion library,
  mocking approach, or an HTTP / infrastructure / browser / BDD / architecture
  tool, and flags the selection tie-breakers and pitfalls that generic knowledge
  misses. Triggers on: assert or compare JSON, extract a value from a JSON
  payload, mock an
  external HTTP API, integration test against a real database/broker/cloud with
  Testcontainers, test asynchronous code, black-box test a REST API, browser or
  end-to-end testing (Playwright vs Selenium), BDD/Gherkin scenarios, enforce
  architecture rules as tests, generate test data, judge test quality beyond
  coverage, decide between JUnit versions (4 vs 5 vs 6) and handle JUnit 6
  migration gotchas, choose between MockK and Mockito on Kotlin, mock a Kotlin
  object or extension function, test Kotlin coroutines/suspend functions and
  Flows (kotlinx-coroutines-test), or fix Java/Kotlin test interop problems in a
  mixed source set.
---

# JVM Testing Toolbox — tool selector

This is a **router**, not a tutorial. Idiomatic use of the tools themselves is
assumed known. The value here is **which tool fits which problem**, the
**tie-breakers** between overlapping tools, and the **pitfalls** that bite.

Distilled from **Philip Riecks — _Java Testing Toolbox: 30 Testing Tools and
Libraries Every Java Developer Must Know_**, then **curated** rather than
mirrored — `README.md` records what was dropped and why. Full credit and links
there. Runnable examples: `github.com/rieckpil/java-testing-ecosystem`. Playwright,
Cucumber, and the Kotlin tools (MockK, kotlinx-coroutines-test) are additions
**beyond the book**, which is Java-framed.

## Scope

Deliberately narrow: what `spring-boot-starter-test` already puts on the classpath,
the few tools reached for constantly on top of it, and the Kotlin tools when the
module has Kotlin. Tools that are excellent but narrow, unmaintained, or displaced
were cut — `README.md` records each one and why. **If the answer isn't in a table
below, that is information**: say so rather than reaching for something off-map.

## Currency

**Last verified: 2026-07** (JUnit 6.0.x era). Routing facts age. If the answer
hinges on a version-sensitive fact — a framework major, a "tool X (doesn't)
support Y" claim, a default that names a release — and time has passed since
the stamp above, spot-check the tool's current release notes before asserting
it. When current docs disagree with a row here, the docs win; say so and note
the row is stale.

## How to use this skill

1. Find the row matching the problem in the tables below.
2. Take the **bold default** unless a tie-breaker condition applies.
3. If the choice is contested or has a known trap, open
   `references/tool-cards.md` (per-tool: purpose + the one high-signal note).
4. Only pull deeper detail when routing has landed — don't preload all cards.

**Java or Kotlin?** These tables apply to both. Where the Kotlin answer differs the
row carries a short **Kotlin:** pointer, and the full decision lives in the **Kotlin
on the JVM** section below. Depth and the Java/Kotlin interop traps are in
`references/kotlin.md`.

**One engine.** In a mixed module run **JUnit Jupiter as the only test engine** —
libraries may differ per file, engines should not. No tool needing a second Platform
engine is listed here — that is a deliberate constraint, not an omission.

## Routing tables

### Test frameworks

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Write a standard unit/integration test on Java 17+ | **JUnit 6 (Jupiter)** | The default for anything new. Align Platform/Jupiter/Vintage via `junit-bom`. |
| Write tests but stuck on Java 8–16 | JUnit 5 (Jupiter) | JUnit 6 needs **Java 17+** (Kotlin 2.2+). Get to 5.14 first — it flags 6.0 removals as deprecations. |
| Maintain a legacy suite on the old API | JUnit 4 | Runs via `junit-vintage-engine` — **deprecated in JUnit 6**; migrate when able. **Never mix JUnit 4 and Jupiter imports in one class** — see pitfalls. |

### Assertion libraries

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Fluent, chainable assertions on any type | **AssertJ** | Default for everything new. Works unchanged from Kotlin. |
| Matcher-style `assertThat(actual, matcher)` | Hamcrest | **You will meet this whether or not you choose it** — Spring MockMvc's `ResultMatchers` are Hamcrest-based. Read it fluently; don't reach for it when writing new assertions. |
| Extract a value from a JSON payload | **JsonPath** | It *extracts* — pair it with an assertion library. |
| Compare a whole JSON document | **JSONAssert** | Whole-document structural compare. **Set `JSONCompareMode` deliberately.** |

### Mocking & stubbing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock/stub collaborators of a class under test | **Mockito** | Default; final classes and statics need no extra dependency. Watch `UnnecessaryStubbingException` (strictness). **Kotlin:** `mockito-kotlin` adds null-safe matchers and `onBlocking`; for `object`s, extension fns or suspending answers see *Kotlin on the JVM*. |

### Mock an external HTTP API

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Stub and verify an outbound HTTP dependency | **WireMock** | Standalone/Docker when the stubs are shared cross-team. Use the Jupiter support (`@WireMockTest` or a registered `WireMockExtension`) rather than hand-rolled `@BeforeAll` lifecycle — stubs reset between tests. |

### Real infrastructure (integration / e2e)

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| A real DB, broker, cache, search index, identity server, cloud emulator — anything that ships as a container | **Testcontainers** | The general answer; prefer it over a bespoke fake or an in-memory substitute that behaves differently from production. Official module where one exists, else `GenericContainer`. **Always set an explicit wait strategy.** On Spring Boot 3.1+ use `@ServiceConnection`. |

### REST API testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Black-box test an HTTP API fluently | **REST Assured** | given/when/then DSL, reusable request/response specs. Its `jsonPath()` is **Groovy GPath, not Jayway JsonPath** — expressions don't carry over from the JsonPath row. |

### Asynchronous code

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Assert on a result that appears eventually | **Awaitility** | **Never `Thread.sleep`.** `ignoreExceptions()` while a resource is still coming up. |

### Browser / end-to-end

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Browser tests for a new suite | **Playwright** (Java binding) | Measurably faster and far less flaky than Selenium in published comparisons. **Tie-breaker:** if the team already has a large, stable Selenium suite and fluency in it, staying there ships faster than a rewrite — migrate new specs, don't big-bang. |

### Behaviour-driven testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Executable specifications in Gherkin, readable by non-engineers | **Cucumber (JVM)** | The reference Gherkin implementation and the safe default. **Only adopt if non-engineers genuinely read the features**; if they don't, plain JUnit + AssertJ is cheaper and clearer than maintaining step definitions. |

### Architecture & test quality

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Enforce layering / no cycles / naming as tests | **ArchUnit** | Rules as JUnit tests. Reads bytecode, so it covers Java and Kotlin alike. |
| Auto-generate random, fully populated test objects | Instancio | Cuts test-data boilerplate; integrates with Bean Validation. |
| Judge whether tests actually verify behavior | **PIT (pitest)** | **Coverage ≠ quality** — surviving mutants reveal tests that execute code without asserting on it. Scope it to changed code to keep runs fast. **Kotlin:** generated `Intrinsics` null checks inflate the report — see pitfalls. |

### Kotlin on the JVM

Every table above applies to Kotlin unchanged. These are the Kotlin-**specific**
choices, all **beyond Riecks' (Java-framed) book**; depth and the mixed-source-set
interop traps are in `references/kotlin.md`.

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock a Kotlin `object`, extension fn, or suspending answer | **MockK** | `mockkObject`, `mockkStatic`, `coEvery { } coAnswers { }`. For ordinary classes Mockito + `mockito-kotlin` is fine. Never two mockers on the same type. |
| Test `suspend` functions / coroutine scheduling | **kotlinx-coroutines-test** | `runTest { }` drives virtual time. Inject dispatchers — don't hardcode `Dispatchers.IO`. **Not** for waiting on real infrastructure — that stays Awaitility. |
| Assert on values a `Flow` emits | **kotlinx-coroutines-test** | **Cold, finite flow:** collect it inside `runTest`. **Hot flow** (`StateFlow`/`SharedFlow`): collect in `TestScope.backgroundScope` with `UnconfinedTestDispatcher`. |
| Fix Java/Kotlin interop in one source set | `references/kotlin.md` | `@JvmStatic` for `@BeforeAll`/`@MethodSource`, platform types weakening null assertions, `internal` friend-paths, PIT noise on Kotlin null checks. |

## Cross-cutting reminders

Silent-failure traps that no single row owns — these corrupt a suite:

- **Don't mix JUnit 4 and Jupiter (JUnit 5/6)** annotations/imports in the same test
  class. Lifecycle callbacks stop firing and tests "pass" without running.
- **Don't mix JUnit 5.x and 6.x artifacts** on one classpath — JUnit 6 unified
  Platform/Jupiter/Vintage under a single version; import the `junit-bom`.
- **Never two mockers on the same type** — Mockito and MockK may coexist in a mixed
  module, but not on one type.
- **`Thread.sleep` is never the answer** — Awaitility for wall-clock waiting,
  `runTest` for coroutine scheduling. They are not interchangeable: virtual time
  cannot wait on a container.

Otherwise take the **bold default**, and deviate only when a tie-breaker in the
row itself clearly applies.
