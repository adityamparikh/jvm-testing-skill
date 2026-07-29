# Tool cards

**Last verified: 2026-07.** Version-sensitive claims below (majors, "no official
X" statements) follow the Currency rule in `SKILL.md` — spot-check release notes
when time has passed.

One card per tool: what it's for and the **one high-signal note** worth loading —
the selection criterion or pitfall you won't reliably get from generic knowledge.
Basic usage is intentionally omitted (it's well-known / in the book). For runnable
code see `github.com/rieckpil/java-testing-ecosystem`.

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
- **TestNG** — choose for `@DataProvider`, `dependsOnMethods`, and built-in
  parallelism (`invocationCount`, `threadPoolSize`, `successPercentage`). Note:
  test suites are configured via XML/YAML.
- **Spock** — Groovy, batteries-included (mock + stub + assertions + data-driven
  in one). Note: `Stub` only returns values; `Mock` also verifies interactions
  (`1 * mock.method()`). Use `@Unroll` + `where:` data tables for parameterized tests.

## Assertion libraries

- **AssertJ** — default fluent assertions. Note: `SoftAssertions` reports *all*
  failures at once; extend `AbstractAssert` for domain-specific assertions.
- **Hamcrest** — matcher style + XPath. Note: **arg order is `assertThat(actual,
  matcher)`** — the reverse of JUnit's `assertEquals(expected, actual)`. Mixing the
  two in one test is confusing.
- **JsonPath (Jayway)** — extract values from JSON strings. Note: supports functions
  (`min/max/avg/sum/length/keys`) and filters (`[?(@.price > 1999)]`). It *extracts*;
  pair it with an assertion library.
- **JSONAssert** — compare a whole JSON document. Note: the third `boolean strict`
  arg (or `JSONCompareMode`) is the crux — **lenient** allows extra fields / any array
  order; **strict** enforces exact fields + array order. Default to lenient for
  non-brittle tests.
- **XMLUnit** — compare/validate XML. Note: `CompareMatcher.isIdenticalTo`,
  `XmlAssert`, XPath node extraction, and XSD validation via `Validator`.

## Mocking

- **Mockito** — default JVM mocking. Note: the *four golden rules* (don't mock types
  you don't own / value objects / everything; show love with your tests) and
  `Strictness`/`UnnecessaryStubbingException` keep tests clean. `mockito-inline` for
  static/constructor mocking.
- **Spock mocks** — use instead of Mockito when the spec is Spock. See Spock card.

## HTTP mocking

- **WireMock** — default when you must match requests richly, verify calls, set
  stub priorities, or run a standalone/Docker mock server. Note: use the official
  Jupiter support — `@WireMockTest` or a registered `WireMockExtension`
  (WireMock 2.31+/3.x) — instead of hand-rolling lifecycle in
  `@BeforeAll`/`@AfterAll`; stubs reset automatically between tests.
- **MockWebServer** — lightweight (part of OkHttp). Note: responses are **FIFO
  `enqueue()`d — matching is by order, not by URL**. Use a `Dispatcher` when you need
  URL/method-based responses or repeated responses.

## Real infrastructure

- **Testcontainers** — default for real dependencies in tests. Note: always set a
  **wait strategy** (`Wait.forHttp(...).forStatusCode`, `Wait.forLogMessage(...)`) —
  the container being "up" ≠ the service being ready. Use the BOM to align module
  versions; Ryuk cleans up.
- **LocalStack** — emulate AWS locally (S3/SQS/SNS/…). Note: seed resources by
  mapping init scripts to `/docker-entrypoint-initaws.d` and gate readiness with
  `Wait.forLogMessage(".*Initialized.*")`; override the AWS SDK endpoint to the
  container's mapped edge port (4566).
- **GreenMail** — sandbox SMTP/IMAP/POP3 mail server. **Conditional — only if the app
  actually sends mail.** Note: `GreenMailExtension`; default ports are offset by
  +3000 (SMTP → 3025) — the single most common source of "connection refused" here.
  Also runnable standalone/Docker. If Testcontainers is already in the build,
  Mailpit/MailHog in a container is the lower-ceremony alternative.
- **MicroShed Testing** — true-to-production tests for Jakarta EE / MicroProfile.
  **Conditional — Jakarta EE / MicroProfile only.** Note: builds on Testcontainers;
  `@MicroShedTest` + `ApplicationContainer` deploy the real app; bring your own
  `Dockerfile` if the runtime isn't built in. Quarkus ships its own `@QuarkusTest`,
  and Spring Boot wants `@SpringBootTest` + Testcontainers — neither should route here.

## Browser / UI

- **Selenide** — default UI testing. Note: auto-waits on `should*` conditions (kills
  most flakiness), auto-downloads the driver (WebDriverManager), auto-screenshots +
  saves page source on failure. `Configuration.*` for browser/size/timeout.
- **Selenium** — low-level control. Note: you own explicit waits (`WebDriverWait` +
  `ExpectedConditions`), `By` selectors, and driver management. Prefer Selenide unless
  you specifically need this level of control.

## REST API

- **REST Assured** — fluent black-box API testing. Note: its `jsonPath()`/`xmlPath()`
  use **Groovy GPath**, *not* the Jayway JsonPath syntax — a common source of
  confusion. Reuse `RequestSpecification`/`ResponseSpecification` across tests.

## Async

- **Awaitility** — poll until a condition holds. Note: `await().atMost(...).until(...)`
  / `.untilAsserted(...)`; `ignoreExceptions()` for transient errors;
  `conditionEvaluationListener` for debugging. Replaces every `Thread.sleep`.

## Performance

- **Gatling** — load testing with a Java/Kotlin/Scala DSL. Note: model the system as
  **open** (users keep arriving) vs **closed** (fixed concurrent users) — it changes
  what the numbers mean. HTML report per run.
- **ApacheBench (`ab`)** — CLI HTTP benchmark. Note: zero code; `-n` total, `-c`
  concurrency, `-p`/`-T` for POST bodies. Good for a quick sanity check, not rich
  scenarios; HTTP HEAD/GET/POST/PUT only.
- **JMH** — JVM microbenchmarking. Note: use it instead of hand-rolled timing —
  it manages warmup, forks, and defeats JIT dead-code elimination that makes naive
  benchmarks lie. Put benchmarks in `src/main/java` and run via the runner.
- **JfrUnit** — assert on Java Flight Recorder events in tests. Note: regression-test
  non-functional behavior (allocation, execution time, socket/thread events) that
  unit tests normally can't see.

## Behavior-driven

- **JGiven** — BDD in plain Java. Note: Stage classes with given/when/then methods,
  shared state via `@ProvidedScenarioState`/`@ExpectedScenarioState`, and readable
  HTML/text reports. No Gherkin, no Groovy.

## Contract testing

- **Pact** — consumer-driven contract testing. Note: the **consumer** defines the
  contract (mock provider) → publish to a **Pact Broker** → the **provider** verifies
  against it; `can-i-deploy` gates deploys. Prevents breaking API changes between
  services without full integration environments.

## Architecture & quality

- **ArchUnit** — architecture rules as tests. Note: needs JUnit (no native TestNG);
  common rules — forbid layer violations, forbid cycles (`SlicesRuleDefinition`),
  enforce naming, and require `LocalDate.now()`/`Instant.now()` to take a `Clock` for
  deterministic tests.
- **Instancio** — generate random, fully populated objects. Note: `Instancio.of(...)`
  with `set`/`ignore`/`generate`; `ofList(...).size(n)`; integrates with Bean
  Validation (JSR 380). Kills test-data boilerplate.
- **PIT (pitest)** — mutation testing. Note: **line coverage lies; mutation score
  doesn't.** Mutates bytecode (no prod-code change), surfaces surviving mutants that
  prove tests don't actually assert behavior. Run against changed code to keep it fast.
