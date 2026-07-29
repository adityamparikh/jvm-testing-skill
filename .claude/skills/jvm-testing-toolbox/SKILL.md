---
name: jvm-testing-toolbox
description: >-
  Use when choosing which JVM testing tool to reach for on a specific challenge
  in a Java and/or Kotlin project — including when both languages share one
  module and source set. Covers picking a test framework, assertion library,
  mocking approach, or an HTTP / infrastructure / browser / BDD / architecture
  tool. Deliberately curated to the tools JVM teams actually run, and flags the
  selection tie-breakers and pitfalls that generic knowledge misses. Triggers
  on: assert or compare JSON, extract a value from a JSON payload, mock an
  external HTTP API, integration test against a real database/broker/cloud with
  Testcontainers, test asynchronous code, black-box test a REST API, browser or
  end-to-end testing (Playwright vs Selenium), BDD/Gherkin scenarios, enforce
  architecture rules as tests, generate test data, judge test quality beyond
  coverage, decide between JUnit versions (4 vs 5 vs 6) and handle JUnit 6
  migration gotchas, choose between MockK and Mockito on Kotlin, mock a Kotlin
  object or extension function, test Kotlin coroutines/suspend functions and
  Flows (kotlinx-coroutines-test, Turbine), write property-based tests in Kotlin
  (Kotest Property), or fix Java/Kotlin test interop problems in a mixed source
  set.
---

# JVM Testing Toolbox — tool selector

This is a **router**, not a tutorial. Assume idiomatic use of well-known tools
(JUnit 5/6, Mockito, AssertJ, MockK) is already known. The value here is **which tool
fits which problem**, the **tie-breakers** between overlapping tools, and the
**pitfalls** that bite in practice.

Distilled from **Philip Riecks — _Java Testing Toolbox: 30 Testing Tools and
Libraries Every Java Developer Must Know_**, then **curated** rather than
mirrored — `README.md` records what was dropped and why. Full credit and links
there. Runnable examples: `github.com/rieckpil/java-testing-ecosystem`. Playwright,
Cucumber, and the Kotlin tools (MockK, kotlinx-coroutines-test, Turbine, Kotest
Property) are additions **beyond the book**, which is Java-framed.

## Scope

Deliberately small, in two groups:

- **Already on your classpath** — what `spring-boot-starter-test` pulls in:
  JUnit, AssertJ, Hamcrest, Mockito, JSONassert, JsonPath, Awaitility. You will
  use these whether or not you choose them, so the notes here are about using
  them *correctly*, not about adopting them.
- **Reached for constantly** — Testcontainers, WireMock, REST Assured,
  Playwright, Cucumber, ArchUnit, Instancio, PIT.
- **If the module has Kotlin** — MockK, kotlinx-coroutines-test, Turbine,
  Kotest Property, plus `references/kotlin.md` for Java/Kotlin interop.

A router is diluted by breadth: every extra destination is one more confident
wrong turn. Tools that are excellent but narrow, unmaintained, or displaced were
cut, not listed. If the answer isn't here, that is information — say so rather
than reaching for something off-map.

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
   `references/tool-cards.md` (per-tool: purpose + the one high-signal note) and
   `references/pitfalls.md` (cross-cutting gotchas + tie-breaker rationale).
4. Only pull deeper detail when routing has landed — don't preload all cards.

**Java or Kotlin?** These tables apply to both. Where Kotlin has an idiomatic swap
the row's note names it (**Kotlin:** …); Kotlin-only concerns (coroutines, `Flow`)
are in the **Kotlin on the JVM** section below. For Kotlin depth and the Java/Kotlin
interop traps, open `references/kotlin.md`.

**One engine.** In a mixed Java+Kotlin module, run **JUnit Jupiter as the only test
engine** — one runner, one report, one CI config. Libraries may differ per file;
engines should not. That is why Kotest appears here as an assertion and
property-testing *library* rather than a framework, and why no tool requiring a
second engine appears at all.

## Routing tables

### Test frameworks

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Write a standard unit/integration test on Java 17+ | **JUnit 6 (Jupiter)** | The default for anything new (GA Sep 2025). Same Jupiter API/packages as JUnit 5; Platform/Jupiter/Vintage now share one 6.x version — align via `junit-bom`. |
| Write tests but stuck on Java 8–16 | JUnit 5 (Jupiter) | Same programming model; JUnit 6 requires **Java 17+** (Kotlin 2.2+). Get to 5.14 first — it flags 6.0 removals as deprecations. |
| Maintain a legacy suite on the old API | JUnit 4 | Runs via `junit-vintage-engine` — **deprecated in JUnit 6**; migrate when able. **Never mix JUnit 4 and Jupiter imports in one class** — see pitfalls. |

### Assertion libraries

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Fluent, chainable assertions on any type | **AssertJ** | Default for everything new. Soft assertions to report all failures at once; custom `AbstractAssert` for domain types. **Kotlin:** `kotest-assertions-core` (`x shouldBe y`) is an idiomatic alternative that needs no Kotest engine; AssertJ itself works unchanged from Kotlin. |
| Matcher-style `assertThat(actual, matcher)` | Hamcrest | **You will meet this whether or not you choose it** — Spring MockMvc's `ResultMatchers` are Hamcrest-based. Arg order is the reverse of JUnit's `assertEquals(expected, actual)`. Read it fluently; don't reach for it when writing new assertions. |
| Extract a value from a JSON payload | **JsonPath** | `$..price.max()`, filters `[?(@.tags.size() > 2)]`. It *extracts* — pair it with an assertion library. |
| Compare a whole JSON document | **JSONAssert** | Verifies logical structure. **Mind `strictMode`/`JSONCompareMode`** — lenient by default; strict enforces array order + no extra fields. |

### Mocking & stubbing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock/stub collaborators of a class under test | **Mockito** | Default. Keep the four golden rules; watch `UnnecessaryStubbingException` (strictness). Since **Mockito 5** the inline mock-maker is the default, so final classes and statics mock with no extra dependency. **Kotlin:** that covers Kotlin's final-by-default classes too, and `mockito-kotlin` adds null-safe matchers plus `onBlocking` for `suspend` functions. Reach for **MockK** for `object`s, extension/top-level fns, or suspending answers needing real control. Never two mockers on the same type. **Beyond the book.** |

### Mock an external HTTP API

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Stub and verify an outbound HTTP dependency | **WireMock** | Request matching on header/body/query, verification (`verify(getRequestedFor(...))`), stub priorities, standalone/Docker for cross-team use. Use the Jupiter support (`@WireMockTest` or a registered `WireMockExtension`) rather than hand-rolled `@BeforeAll` lifecycle — stubs reset between tests. |

### Real infrastructure (integration / e2e)

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| A real DB, broker, cache, search index, identity server, cloud emulator — anything that ships as a container | **Testcontainers** | The general answer; prefer it over a bespoke fake or an in-memory substitute that behaves differently from production. Use the official module when one exists (`PostgreSQLContainer`, `KafkaContainer`, `LocalStackContainer`…), otherwise `GenericContainer` with an image. **Always set a wait strategy** (`Wait.forHttp`, `Wait.forLogMessage`) — "container started" ≠ "service ready". Align versions with the Testcontainers BOM. On Spring Boot 3.1+, `@ServiceConnection` wires the container to your properties automatically. |

### REST API testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Black-box test an HTTP API fluently | **REST Assured** | given/when/then DSL, reusable request/response specs. Its `jsonPath()` uses **Groovy GPath, not Jayway JsonPath** — don't copy `$..` expressions into it. |

### Asynchronous code

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Assert on a result that appears eventually | **Awaitility** | `await().atMost(...).until(...)` / `.untilAsserted(...)`. **Never `Thread.sleep`.** `ignoreExceptions()` while a resource is still coming up. |

### Browser / end-to-end

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Browser tests for a new suite | **Playwright** (Java binding) | Auto-waiting, one API across Chromium/Firefox/WebKit, tracing and codegen built in. Measurably faster and far less flaky than Selenium in published comparisons. **Tie-breaker:** if the team already has a large, stable Selenium suite and fluency in it, staying there ships faster than a rewrite — migrate new specs, don't big-bang. |

### Behaviour-driven testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Executable specifications in Gherkin, readable by non-engineers | **Cucumber (JVM)** | The reference Gherkin implementation and the safe default. Run 7.x via the **JUnit 5 Platform Suite** (`@Suite` + `@IncludeEngines("cucumber")`) — not the legacy JUnit 4 runner. **Only adopt if non-engineers genuinely read the features**; if they don't, plain JUnit + AssertJ is cheaper and clearer than maintaining step definitions. |

### Architecture & test quality

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Enforce layering / no cycles / naming as tests | **ArchUnit** | Rules as JUnit tests; e.g. "services must not depend on controllers", "`LocalDate.now()` must take a `Clock`". Reads bytecode, so it covers Java and Kotlin alike. |
| Auto-generate random, fully populated test objects | Instancio | Cuts test-data boilerplate; `set`/`ignore`/`generate`, `ofList(n)`; integrates with Bean Validation. |
| Generate inputs and assert an invariant holds (Kotlin) | **Kotest Property** | `checkAll` + `Arb` via `kotest-property` alone — runs inside a Jupiter `@Test`, no Kotest engine, one engine preserved. Shrinks failures to a minimal counterexample. No Java-side entry: jqwik would add a second Platform engine, is in maintenance mode, and carries an Anti-AI Usage Clause. **Beyond the book.** |
| Judge whether tests actually verify behavior | **PIT (pitest)** | **Coverage ≠ quality.** Mutates bytecode; surviving mutants reveal tests that execute code without asserting on it. Scope it to changed code to keep runs fast. On Kotlin, generated `Intrinsics` null checks inflate the report — see pitfalls. |

### Kotlin on the JVM

Every table above applies to Kotlin unchanged. These are the Kotlin-**specific**
choices — a swap for a shared concern, plus axes with no Java equivalent. All are
**beyond Riecks' (Java-framed) book**; depth and the mixed-source-set interop traps
are in `references/kotlin.md`.

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock a Kotlin `object`, extension fn, or suspending answer | **MockK** | `mockkObject`, `mockkStatic`, `coEvery { } coAnswers { }`. For ordinary classes Mockito 5 + `mockito-kotlin` is fine — final classes mock by default, `onBlocking` stubs `suspend` fns. Never two mockers on the same type. |
| Test `suspend` functions / coroutine scheduling | **kotlinx-coroutines-test** | `runTest { }` drives virtual time; advance with `advanceUntilIdle()` / `runCurrent()`. Inject dispatchers — don't hardcode `Dispatchers.IO`. **Not** for waiting on real infrastructure — that stays Awaitility. |
| Assert on values a `Flow` emits | **Turbine** | `flow.test { awaitItem(); awaitComplete() }` — fails on unconsumed items, unlike a plain `toList()` collect. Pairs with any assertion lib. |
| Fix Java/Kotlin interop in one source set | `references/kotlin.md` | `@JvmStatic` for `@BeforeAll`/`@MethodSource`, platform types weakening null assertions, `internal` friend-paths, PIT noise on Kotlin null checks. |

## Cross-cutting reminders

- **Don't mix JUnit 4 and Jupiter (JUnit 5/6)** annotations/imports in the same test class.
- **Don't mix JUnit 5.x and 6.x artifacts** on one classpath — JUnit 6 unified
  Platform/Jupiter/Vintage under a single version; import the `junit-bom`.
- **Awaitility over `Thread.sleep`** for anything asynchronous.
- **One engine in a mixed module** — JUnit Jupiter runs both languages. Bring Kotest
  in as a library (assertions, property testing), never as a second engine.
- **Kotlin mocking: choose per type, not per module.** Mockito 5 + `mockito-kotlin`
  covers most Kotlin; **MockK** for `object`s, extension fns, and suspending answers.
  Never two mockers on the same type.
- **Kotlin coroutines: `runTest` + an injected `TestDispatcher`**, never real delays
  or `Thread.sleep`; **Turbine** for `Flow`. Waiting on real infrastructure is still
  **Awaitility** — virtual time cannot wait on a container.
- **Testcontainers over hand-rolled fakes** when the dependency has an image —
  and always with an explicit wait strategy.
- **PIT/mutation score, not line coverage**, is the real test-quality signal.
- **AssertJ for new assertions**; read Hamcrest, don't write it.
- Prefer the **bold default**; deviate only when a tie-breaker condition in
  `references/pitfalls.md` clearly applies.
