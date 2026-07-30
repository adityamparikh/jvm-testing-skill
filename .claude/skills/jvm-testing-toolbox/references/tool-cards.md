# Tool cards

**Last verified: 2026-07.** Version-sensitive claims below (majors, "no official
X" statements) follow the Currency rule in `SKILL.md` — spot-check release notes
when time has passed.

One card per tool: what it's for and the **one high-signal note** worth loading —
the selection criterion or pitfall you won't reliably get from generic knowledge.
Basic usage is intentionally omitted (it's well-known / in the book). For runnable
code see `github.com/rieckpil/java-testing-ecosystem`.

The set is curated, not exhaustive — see `README.md` for what was cut and why.

## Test frameworks

- **JUnit 6 (Jupiter)** — default framework for Java 17+ (GA 2025-09-30). Note:
  same Jupiter API/packages as JUnit 5, so from 5.14 + Java 17 it's mostly a
  version bump — the traps are elsewhere: Platform/Jupiter/Vintage now share one
  6.x version (use `junit-bom`; mixed 5.x/6.x artifacts break), the CSV engine
  behind `@CsvSource`/`@CsvFileSource` changed to FastCSV, and
  `junit-platform-runner` is gone. Gains: Kotlin `suspend` test methods, JSpecify
  nullability, fail-fast/`CancellationToken`, JFR support built into the launcher.
- **JUnit 5 (Jupiter)** — same programming model when stuck on **Java 8–16**
  (JUnit 6 requires 17+). Note: classes/methods can be package-private; the
  extension model (`@ExtendWith`, `ParameterResolver`) replaces JUnit 4
  runners + rules. Get to 5.14 before jumping to 6 — it flags 6.0 removals as
  deprecations.
- **JUnit 4** — legacy only. Note: uses runners (`@RunWith`) and rules
  (`@Rule`/`@ClassRule`); needs `junit-vintage-engine` to run under the JUnit
  Platform — **deprecated in JUnit 6** (reports a discovery issue per JUnit 4
  class found). Migrate forward.

## Assertion libraries

- **AssertJ** — default fluent assertions for anything new. Note: `SoftAssertions`
  reports *all* failures at once instead of stopping at the first; extend
  `AbstractAssert` for domain-specific assertions that read like the domain.
- **Hamcrest** — matcher style. Note: **you will meet it whether or not you pick
  it** — Spring MockMvc's `ResultMatchers` are Hamcrest-based, so `andExpect`
  chains are Hamcrest even in an AssertJ codebase. Arg order is
  `assertThat(actual, matcher)` — the reverse of JUnit's `assertEquals(expected,
  actual)`. Read it; don't write new assertions in it.
- **JsonPath (Jayway)** — extract values from JSON strings. Note: supports functions
  (`min/max/avg/sum/length/keys`) and filters (`[?(@.price > 1999)]`). It *extracts*;
  pair it with an assertion library.
- **JSONAssert** — compare a whole JSON document. Note: the third `boolean strict`
  arg (or `JSONCompareMode`) is the crux — **lenient** allows extra fields / any array
  order; **strict** enforces exact fields + array order. Default to lenient for
  non-brittle tests.

## Mocking

- **Mockito** — default JVM mocking. Note: the *four golden rules* (don't mock types
  you don't own / value objects / everything; show love with your tests) and
  `Strictness`/`UnnecessaryStubbingException` keep tests clean. Since **Mockito 5**
  the inline mock-maker is the **default in `mockito-core`** — final classes, statics
  and constructors mock with no extra dependency, and the separate `mockito-inline`
  artifact is no longer needed (it stopped being published after 5.2).

## HTTP mocking

- **WireMock** — stub and verify outbound HTTP. Note: use the official Jupiter
  support — `@WireMockTest` or a registered `WireMockExtension` (WireMock 2.31+/3.x)
  — instead of hand-rolling lifecycle in `@BeforeAll`/`@AfterAll`; stubs reset
  automatically between tests. Reach for verification (`verify(getRequestedFor(...))`)
  when the *request* is the thing under test, not just the response.

## Real infrastructure

- **Testcontainers** — the general answer for any dependency that ships as a
  container: databases, brokers, caches, search indexes, identity servers, cloud
  emulators. Note: always set a **wait strategy**
  (`Wait.forHttp(path).forStatusCode(200)`, `Wait.forLogMessage(regex, n)`) — the
  container being "up" ≠ the service being ready, and that race is the single most
  common source of flaky integration tests. Use official modules where they exist,
  `GenericContainer` otherwise; align versions with the Testcontainers BOM; Ryuk
  cleans up. On Spring Boot 3.1+, `@ServiceConnection` wires the container into
  application properties so you stop hand-mapping ports and URLs.

## REST API

- **REST Assured** — fluent black-box API testing. Note: its `jsonPath()`/`xmlPath()`
  use **Groovy GPath**, *not* the Jayway JsonPath syntax — a common source of
  confusion. Reuse `RequestSpecification`/`ResponseSpecification` across tests.

## Async

- **Awaitility** — poll until a condition holds. Note: `await().atMost(...).until(...)`
  / `.untilAsserted(...)`; `ignoreExceptions()` for transient errors;
  `conditionEvaluationListener` for debugging. Replaces every `Thread.sleep`.

## Browser / end-to-end

- **Playwright (Java)** — default for new browser suites. Note: auto-waiting is the
  point — locators retry until actionable, which removes the explicit-wait
  boilerplate that causes most Selenium flakiness. One API across
  Chromium/Firefox/WebKit; `trace.zip` gives a time-travel debugger for CI failures;
  `codegen` records a starting script. **Tie-breaker:** an existing large, stable
  Selenium suite plus team fluency beats a rewrite — add new specs in Playwright
  rather than migrating wholesale.

## Behaviour-driven

- **Cucumber (JVM)** — executable specifications in Gherkin. Note: run 7.x through
  the **JUnit 5 Platform Suite** (`@Suite` + `@IncludeEngines("cucumber")`), not the
  legacy JUnit 4 runner. The real selection criterion is social, not technical:
  **adopt it only if non-engineers actually read and write the feature files.** If
  they don't, you are paying for a step-definition indirection layer that buys
  nothing over plain JUnit + AssertJ.

## Architecture & quality

- **ArchUnit** — architecture rules as tests. Note: needs JUnit; common rules —
  forbid layer violations, forbid cycles (`SlicesRuleDefinition`), enforce naming,
  and require `LocalDate.now()`/`Instant.now()` to take a `Clock` for deterministic
  tests. Reads **bytecode**, so the same rules cover Java and Kotlin.
- **Instancio** — generate random, fully populated objects. Note: `Instancio.of(...)`
  with `set`/`ignore`/`generate`; `ofList(...).size(n)`; integrates with Bean
  Validation (JSR 380). Kills test-data boilerplate — and randomised values surface
  assumptions a hand-built fixture would have hidden.
- **PIT (pitest)** — mutation testing. Note: **line coverage lies; mutation score
  doesn't.** Mutates bytecode (no prod-code change), surfacing surviving mutants that
  prove a test ran the code without asserting on the result. Run against changed code
  to keep it fast; triage equivalent mutants separately.

## Kotlin (beyond the book)

The book is Java-framed; these are additions, included because real JVM projects mix
Java and Kotlin — often in one source set. Depth and the interop traps live in
`references/kotlin.md`.

- **MockK** — idiomatic Kotlin mocking. Note: reach for it over Mockito when you need
  `object` singletons (`mockkObject`), top-level/extension functions (`mockkStatic`),
  or *suspending* answers with real control (`coEvery { } coAnswers { }`) — **not**
  merely to mock final classes, which Mockito 5 does by default. `relaxed = true` /
  `@RelaxedMockK` avoids stubbing every call. In a mixed module the rule is **never
  two mockers on the same type**, not "one mocker per module".
- **kotlinx-coroutines-test** — test `suspend`/coroutine code. Note: `runTest { }`
  uses a virtual-time scheduler so `delay()` is skipped and tests stay deterministic.
  `StandardTestDispatcher` queues coroutines (advance with
  `advanceUntilIdle()`/`runCurrent()`); `UnconfinedTestDispatcher` runs them eagerly.
  Inject dispatchers into production code — a hardcoded `Dispatchers.IO` can't be
  swapped for a `TestDispatcher`. **Not** a substitute for Awaitility: virtual time
  cannot wait on a real container or HTTP endpoint. **`Flow` testing lives here too**
  — cold flows via `toList()` inside `runTest`, hot flows via
  `TestScope.backgroundScope`; no separate library needed. See `kotlin.md`.
