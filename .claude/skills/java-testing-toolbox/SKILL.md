---
name: java-testing-toolbox
description: >-
  Use when choosing which Java/JVM testing tool to reach for on a specific
  challenge — picking a test framework, assertion library, mocking approach, or
  an HTTP / infrastructure / UI / performance / contract / architecture tool.
  Routes a testing problem to the right tool from Philip Riecks' "Java Testing
  Toolbox" and flags the selection tie-breakers and pitfalls that generic
  knowledge misses. Triggers on: assert JSON or XML, mock an external HTTP API,
  integration test with a real database/broker/cloud, test asynchronous code,
  load-test or microbenchmark, contract-test microservices, enforce architecture
  rules, generate test data, judge test quality beyond coverage, or decide
  between JUnit versions (4 vs 5 vs 6) and handle JUnit 6 migration gotchas.
---

# Java Testing Toolbox — tool selector

This is a **router**, not a tutorial. Assume idiomatic use of well-known tools
(JUnit 5, Mockito, AssertJ) is already known. The value here is **which tool
fits which problem**, the **tie-breakers** between overlapping tools, and the
**pitfalls** that bite in practice.

Distilled from **Philip Riecks — _Java Testing Toolbox: 30 Testing Tools and
Libraries Every Java Developer Must Know_**. Full credit and links in the repo
`README.md`. Runnable examples: `github.com/rieckpil/java-testing-ecosystem`.

## How to use this skill

1. Find the row matching the problem in the tables below.
2. Take the **bold default** unless a tie-breaker condition applies.
3. If the choice is contested or has a known trap, open
   `references/tool-cards.md` (per-tool: purpose + the one high-signal note) and
   `references/pitfalls.md` (cross-cutting gotchas + tie-breaker rationale).
4. Only pull deeper detail when routing has landed — don't preload all cards.

Rows marked **Conditional** answer a narrow problem. Reach for them only when that
exact problem is yours — never as a default, and never by analogy.

## Currency

**Last verified: 2026-07** (JUnit 6.0.x era). Routing facts age. If the answer
hinges on a version-sensitive fact — a framework major, a "tool X (doesn't)
support Y" claim, a default that names a release — and time has passed since
the stamp above, spot-check the tool's current release notes before asserting
it. When current docs disagree with a row here, the docs win; say so and note
the row is stale.

## Routing tables

### Test frameworks

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Write a standard unit/integration test on Java 17+ | **JUnit 6 (Jupiter)** | The default for anything new (GA Sep 2025). Same Jupiter API/packages as JUnit 5; Platform/Jupiter/Vintage now share one 6.x version — align via `junit-bom`. |
| Write tests but stuck on Java 8–16 | JUnit 5 (Jupiter) | Same programming model; JUnit 6 requires **Java 17+** (Kotlin 2.2+). |
| Maintain a legacy suite on the old API | JUnit 4 | Runs via `junit-vintage-engine` — **deprecated in JUnit 6**; migrate when able. **Never mix JUnit 4 and Jupiter imports in one class** — see pitfalls. |
| Data-driven params, test ordering, parallel groups | TestNG | `@DataProvider`, `dependsOnMethods`, `invocationCount`/`threadPoolSize`. |
| BDD style with built-in mocking + rich assertions | Spock (Groovy) | given/when/then blocks, data tables, `Mock()`/`Stub()`, `1 * mock.call()`. No separate mock/assert libs needed. |

### Assertion libraries

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Fluent, chainable assertions on any type | **AssertJ** | Default. Soft assertions to report all failures; custom `AbstractAssert` for domain types. |
| Matcher-style / `Matchers.*`, or XPath assertions | Hamcrest | Note arg order: `assertThat(actual, matcher)` (opposite of JUnit's `assertEquals(expected, actual)`). |
| Extract a value from a JSON payload | JsonPath | `$..price.max()`, filters `[?(@.tags.size() > 2)]`. Pairs with any assertion lib. |
| Compare a whole JSON document | **JSONAssert** | Verifies logical structure. **Mind `strictMode`/`JSONCompareMode`** — lenient by default; strict enforces array order + no extra fields. |
| Compare / XPath / schema-validate XML | XMLUnit | `isIdenticalTo`, XPath node extraction, XSD validation. |

### Mocking & stubbing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Mock/stub collaborators of a class under test | **Mockito** | Default. Keep the four golden rules; watch `UnnecessaryStubbingException` (strictness). Use `ArgumentMatchers`, `thenAnswer`, `verify`. |
| Mock while already writing Spock specs | Spock built-in `Mock`/`Stub` | Don't add Mockito to a Spock spec. `Stub` = only return values; `Mock` = also verify interactions. |

### Mock an external HTTP API

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Rich request matching, verification, priorities, standalone/Docker | **WireMock** | Default when you need to *assert* on requests or run a shared mock server. |
| Lightweight, dependency-light HTTP stub | MockWebServer | FIFO `enqueue()` (order matters, not URL) or a `Dispatcher`. Ships with OkHttp; feels lighter than WireMock. |

### Real infrastructure (integration / e2e)

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| A real DB / Kafka / Keycloak / any Dockerized dependency | **Testcontainers** | Default for integration infra. Use modules (PostgreSQLContainer…) and a **wait strategy** (`Wait.forHttp`, `forLogMessage`) or the container reports ready too early. |
| Emulate AWS (S3/SQS/SNS/SSM…) locally | LocalStack | Via the Testcontainers module; seed infra with an init script in `/docker-entrypoint-initaws.d` + `Wait.forLogMessage`. |
| Test sending/receiving email (SMTP/IMAP/POP3) | GreenMail | **Conditional — only if the app sends mail.** Sandbox mail server; `GreenMailExtension`; default ports offset +3000. Alternative: Testcontainers + Mailpit/MailHog if you already run Testcontainers. |
| Test a Jakarta EE / MicroProfile app in-container | MicroShed Testing | **Conditional — Jakarta EE / MicroProfile only.** Builds on Testcontainers; `@MicroShedTest` deploys the app to a real server. On Quarkus prefer native `@QuarkusTest`; on Spring Boot this does not apply — use `@SpringBootTest` + Testcontainers. |

### Browser / UI

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Concise, reliable UI tests | **Selenide** | Default. Auto-waits on conditions, auto-manages the driver, auto-screenshots on failure. `$(...).shouldHave(text(...))`. |
| Low-level browser control / custom protocol work | Selenium | More boilerplate: explicit `WebDriverWait`, `By` selectors, driver setup (WebDriverManager). Choose only when Selenide's abstraction is limiting. |

### REST API testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Black-box test an HTTP API fluently | **REST Assured** | given/when/then DSL, JSON/XML path assertions, reusable request/response specs. Uses Groovy GPath (not Jayway JsonPath) internally. |

### Asynchronous code

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Assert on a result that appears eventually | **Awaitility** | `await().atMost(...).until(...)`. **Never `Thread.sleep`.** `ignoreExceptions()` for transient failures. |

### Performance & benchmarking

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Load-test an API/service | **Gatling** | Java/Kotlin DSL; model as open (arrivals) vs closed (fixed users) system. |
| Quick one-off HTTP throughput/latency from the CLI | ApacheBench (`ab`) | No code; `-n`/`-c`. Good for a fast sanity benchmark. |
| Microbenchmark a JVM method accurately | JMH | Handles warmup/JIT/dead-code elimination that naive `System.nanoTime()` gets wrong. |
| Assert on runtime behavior via Flight Recorder events | JfrUnit | Regression-test allocations, execution time, thread contention through JFR events. |

### Behavior-driven testing

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| BDD scenarios in **plain Java** with readable reports | **JGiven** | given/when/then Stage classes, `@ScenarioStage`, HTML/text reports. Stay in Java (no Groovy/Gherkin). |
| BDD when already on Groovy | Spock | See test frameworks. |

### Contract testing (microservices)

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Verify consumer↔provider API compatibility | **Pact** | Consumer-driven contracts, Pact Broker, `can-i-deploy`. Catches breaking API changes before deploy. |

### Architecture & test quality

| I need to… | Reach for | Tie-breaker / note |
|---|---|---|
| Enforce layering / no cycles / naming as tests | **ArchUnit** | Rules as JUnit tests; e.g. "services must not depend on controllers", "`LocalDate.now()` must take a `Clock`". |
| Auto-generate random, fully populated test objects | Instancio | Cuts test-data boilerplate; override/ignore fields; integrates with Bean Validation. |
| Judge whether tests actually verify behavior | **PIT (pitest)** | **Coverage ≠ quality.** Mutates bytecode; surviving mutants reveal weak tests. Run on changed code. |

## Cross-cutting reminders

- **Don't mix JUnit 4 and Jupiter (JUnit 5/6)** annotations/imports in the same test class.
- **Don't mix JUnit 5.x and 6.x artifacts** on one classpath — JUnit 6 unified
  Platform/Jupiter/Vintage under a single version; import the `junit-bom`.
- **Awaitility over `Thread.sleep`** for anything asynchronous.
- **PIT/mutation score, not line coverage**, is the real test-quality signal.
- Prefer the **book-default in bold**; deviate only when a tie-breaker condition
  in `references/pitfalls.md` clearly applies.
