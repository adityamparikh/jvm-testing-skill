# Pitfalls & tie-breaker rationale

**Last verified: 2026-07.** Version-sensitive claims follow the Currency rule in
`SKILL.md`.

Load this when a routing choice is contested or a known trap applies. These are the
mistakes and decision points the base model tends to miss.

## Framework pitfalls

- **Never mix JUnit 4 and Jupiter in one class.** `org.junit.Test` (4) and
  `org.junit.jupiter.api.Test` (5/6) look identical at a glance and cause silent,
  weird failures — lifecycle callbacks not firing, tests "passing" without running.
  Pick one per class. With Spring Boot on the classpath this is easy to do by accident.
- Jupiter test classes/methods can be **package-private** — don't add `public` out of
  JUnit 4 habit.

## JUnit 6 migration pitfalls

- **Don't mix 5.x and 6.x artifacts.** JUnit 6 unified versioning: Platform, Jupiter,
  and Vintage all ship as 6.x (no more platform 1.x vs jupiter 5.x). A 5.x
  `junit-platform-launcher` with 6.x Jupiter (or vice versa, often dragged in
  transitively by build-tool or IDE plugins) breaks discovery. Import the
  `junit-bom` and let it pin everything.
- **Java 17+ / Kotlin 2.2+ required.** On Java 8–16, stay on JUnit 5 — same Jupiter
  API, so migrate the JDK first, then bump JUnit.
- **Upgrade via 5.14 first.** 5.14 flags everything 6.0 removed as deprecated —
  fix those warnings and 6.0 is close to a version bump.
- **Vintage engine is deprecated in 6** (it logs a discovery issue per JUnit 4 class)
  and frameworks are dropping its dependency management (e.g. Spring Boot 4 no longer
  manages it) — declare and version it explicitly if you still need it, and treat it
  as migration scaffolding, not a destination. `junit-platform-runner` (running
  Platform tests *under* JUnit 4) is **removed**.
- **Parameterized CSV behavior changed** — JUnit 6 swapped univocity-parsers for
  FastCSV: `lineSeparator` is gone from `@CsvFileSource` (auto-detected now) and
  stray characters after a closing quote are rejected. Quirky `@CsvSource` data that
  passed on 5.x can fail on 6.x.
- **With Spring Boot, take the Boot-managed JUnit line** — Boot 3.5.x manages
  JUnit 5, Boot 4.x manages JUnit 6. Overriding the managed version means owning
  `junit-bom` alignment yourself; prefer upgrading Boot to get JUnit 6.

## Assertion pitfalls

- **`assertThat` argument order differs by library.** Hamcrest/AssertJ:
  `assertThat(actual)...`. JUnit's `assertEquals(expected, actual)`. Mixing Hamcrest
  and AssertJ `assertThat` imports in one test is a foot-gun — be deliberate.
- **JSONAssert strictness is the whole game.** The `boolean strict` / `JSONCompareMode`
  decides whether extra fields and array ordering fail the test. Default to **lenient**
  so tests aren't brittle; go strict only to pin exact structure/order.
- **REST Assured uses Groovy GPath, not Jayway JsonPath.** `[0].orders.size()` and
  closures like `find{...}` — not `$..orders`. Don't copy Jayway expressions into it.

## Mocking pitfalls

- **`UnnecessaryStubbingException`** fires when a stubbed call is never used — it's a
  feature (dead stub = unclear test). Fix the stub, or drop to `Strictness.LENIENT`
  deliberately, not reflexively.
- **Don't add Mockito to a Spock spec** — Spock has `Mock`/`Stub` built in. In Spock,
  `Stub` = return values only; `Mock` = also verify interactions. A `Mock` can act as
  a `Stub`, not vice-versa.

## HTTP mocking tie-breaker (WireMock vs MockWebServer)

- **WireMock** when you need: request matching on headers/body/query, verification
  (`verify(getRequestedFor(...))`), stub priorities, or a standalone/Docker server
  shared across languages. Richer, slightly heavier.
- **MockWebServer** when you want minimal footprint (it ships with OkHttp) and simple
  scripted responses. Responses are **enqueued FIFO — served by order, not by URL**;
  reach for a `Dispatcher` when you need URL/method routing or repeated responses.

## Infrastructure pitfalls

- **Testcontainers readiness ≠ container started.** Always set an explicit wait
  strategy (`Wait.forHttp(path).forStatusCode(200)`, `Wait.forLogMessage(regex, n)`),
  or tests race the service. Align module versions with the Testcontainers BOM.
- **LocalStack seeding + endpoint override.** Put setup scripts in
  `/docker-entrypoint-initaws.d`, gate readiness on their log output
  (`Wait.forLogMessage(".*Initialized.*", 1)`), and point the AWS SDK at the mapped
  edge port (4566) — it's randomized by Testcontainers, so read it dynamically.
- **GreenMail default ports are offset +3000** (SMTP 25 → 3025, IMAP → 3143, …).

## UI tie-breaker (Selenide vs Selenium)

- **Selenide by default.** Its `should*` conditions auto-wait (removes the #1 cause of
  UI flakiness), it auto-manages the driver, and it screenshots + dumps page source on
  failure. Far less boilerplate.
- **Selenium** only when you need low-level control Selenide abstracts away (custom
  protocols, fine-grained wait/driver tuning). Then you own `WebDriverWait` +
  `ExpectedConditions`.

## Async pitfall

- **`Thread.sleep` in async tests is always wrong** — it's slow *and* flaky. Use
  **Awaitility**: `await().atMost(...).until(...)` or `.untilAsserted(...)`. Use
  `ignoreExceptions()` while the resource is still coming up.

## Performance tie-breakers

- **ApacheBench** = 30-second CLI sanity check (throughput/latency).
- **Gatling** = real load scenarios with a code DSL and reports; decide open vs closed
  workload model deliberately.
- **JMH** = *method-level* microbenchmarks — never hand-roll with `System.nanoTime()`,
  the JIT will make naive benchmarks meaningless.
- **JfrUnit** = assert on runtime/JFR behavior (allocations, latency, contention).

## Test-quality pitfall

- **Line/branch coverage does not measure whether tests assert anything.** A test can
  execute code and verify nothing. **PIT mutation testing** is the real signal: if a
  mutant survives, some test ran the code but didn't check the result. Run PIT on
  changed code (scoped) to keep it fast; triage equivalent mutants separately.

## Architecture pitfall

- **Non-deterministic `now()`.** Tests that call `LocalDate.now()`/`Instant.now()`
  without an injected `Clock` are time-flaky. Enforce it with an **ArchUnit** rule so
  the whole codebase stays testable, not just the file you're editing.
