# Tool cards

**Last verified: 2026-07.** Version-sensitive claims below (majors, "no official
X" statements) follow the Currency rule in `SKILL.md` — spot-check release notes
when time has passed.

One card per tool: what it's for and the **one high-signal note** worth loading —
the selection criterion or pitfall you won't reliably get from generic knowledge.
If the note is something you would apply anyway, the tool gets **no card**: Mockito
(default JVM mocking), AssertJ (default assertions), Jayway JsonPath (extraction),
REST Assured (black-box API), Awaitility (poll instead of `Thread.sleep`) and
ArchUnit (architecture rules as tests) are still the right defaults — they just
need nothing loaded. Runnable code: `github.com/rieckpil/java-testing-ecosystem`.

The set is curated, not exhaustive — see `README.md` for what was cut and why.

## Test frameworks

- **JUnit 6 (Jupiter)** — default framework for **Java 17+** (GA 2025-09-30).
  Note: same Jupiter API/packages as JUnit 5, so from 5.14 on Java 17 it is mostly
  a version bump — the traps are version alignment and removals:
  Platform/Jupiter/Vintage now share one 6.x version (use `junit-bom`; mixed
  5.x/6.x artifacts break), `junit-platform-runner` is gone, and the CSV engine
  behind `@CsvSource`/`@CsvFileSource` changed to FastCSV — which drops
  `lineSeparator` from `@CsvFileSource` (auto-detected now) and rejects stray
  characters after a closing quote, so quirky CSV data that passed on 5.x fails.
  With Spring Boot, take the Boot-managed line: Boot 3.5.x manages JUnit 5,
  Boot 4.x manages JUnit 6.
- **JUnit 5 (Jupiter)** — the same programming model for projects stuck on
  **Java 8–16**, which cannot use JUnit 6 (**JUnit 6 requires Java 17+**). Note:
  get to **5.14** before jumping to 6 — 5.14 reports the 6.0 removals as
  deprecations, so they surface at compile time rather than on the 6.0 upgrade.
- **JUnit 4** — legacy only. Note: `junit-vintage-engine` still runs it under the
  JUnit Platform but is **deprecated in JUnit 6** (one discovery issue per JUnit 4
  class found), and frameworks have stopped managing its version — Spring Boot 4
  no longer does — so declare and version it explicitly or the build breaks in a
  way that reads as unrelated. Migration scaffolding, not a destination.

## Assertion libraries

- **JSONAssert** — compare a whole JSON document. Note: the third `boolean strict`
  arg (or `JSONCompareMode`) is the entire decision — **lenient** allows extra
  fields and any array order and is the default for non-brittle tests; **strict**
  enforces exact fields plus array order.
- **Hamcrest** — matcher style. Note: **you will meet it whether or not you pick
  it** — Spring MockMvc's `ResultMatchers` are Hamcrest-based, so `andExpect`
  chains are Hamcrest even in an AssertJ codebase, and arg order is
  `assertThat(actual, matcher)`. Read it; don't write new assertions in it.

## HTTP mocking

- **WireMock** — stub and verify outbound HTTP. Note: use the official Jupiter
  support — `@WireMockTest` or a registered `WireMockExtension` (WireMock 2.31+/3.x)
  — instead of hand-rolling lifecycle in `@BeforeAll`/`@AfterAll`; stubs then reset
  automatically between tests.

## Real infrastructure

- **Testcontainers** — the general answer for any dependency that ships as a
  container. Note: always declare an explicit wait strategy
  (`Wait.forHttp(path).forStatusCode(200)`, `Wait.forLogMessage(regex, n)`) — the
  container being "up" ≠ the service being ready, the single most common source of
  flaky integration tests.

## Browser / end-to-end

- **Playwright (Java)** — default for new browser suites. Note: auto-waiting is the
  point — locators retry until actionable, which removes the explicit-wait
  boilerplate that causes most Selenium flakiness. One API across
  Chromium/Firefox/WebKit; `trace.zip` gives a time-travel debugger for CI failures;
  `codegen` records a starting script. **Tie-breaker:** an existing large, stable
  Selenium suite plus team fluency beats a rewrite — add new specs in Playwright
  rather than migrating wholesale.

## Behaviour-driven

- **Cucumber (JVM)** — executable specifications in Gherkin. Note: the real
  selection criterion is social, not technical — **adopt it only if non-engineers
  actually read and write the feature files**; otherwise you pay for a
  step-definition indirection layer that buys nothing over plain JUnit + AssertJ.
  (Run 7.x through the JUnit 5 Platform Suite: `@Suite` +
  `@IncludeEngines("cucumber")`, not the legacy JUnit 4 runner.)

## Test data & quality

- **Instancio** — generate random, fully populated objects. Note: randomised values
  surface assumptions a hand-built fixture would have hidden.
- **PIT (pitest)** — mutation testing. Note: **line coverage lies; mutation score
  doesn't** — surviving mutants prove a test ran the code without asserting on the
  result. Run against changed code to keep it fast.

## Kotlin (beyond the book)

The book is Java-framed; these are additions, included because real JVM projects mix
Java and Kotlin — often in one source set. Depth and the interop traps live in
`references/kotlin.md`.

- **MockK** — idiomatic Kotlin mocking. Note: reach for it over Mockito when you need
  `object` singletons (`mockkObject`), top-level/extension functions (`mockkStatic`),
  or *suspending* answers with real control (`coEvery { } coAnswers { }`) — **not**
  merely to mock final classes, which Mockito 5 does by default. In a mixed module
  the rule is **never two mockers on the same type**, not "one mocker per module".
- **kotlinx-coroutines-test** — test `suspend`/coroutine code. Note: `runTest { }`
  uses a virtual-time scheduler so `delay()` is skipped — which means it is **not** a
  substitute for Awaitility (virtual time cannot wait on a real container or HTTP
  endpoint), and production code must take an injected dispatcher, since a hardcoded
  `Dispatchers.IO` can't be swapped for a `TestDispatcher`
  (`StandardTestDispatcher` queues, advance with `advanceUntilIdle()`/`runCurrent()`;
  `UnconfinedTestDispatcher` runs eagerly). `Flow` testing lives here too — cold flows
  via `toList()` inside `runTest`, hot flows via `TestScope.backgroundScope`. See
  `kotlin.md`.
