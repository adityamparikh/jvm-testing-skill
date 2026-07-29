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

- **`assertThat` argument order differs by library.** Hamcrest: `assertThat(actual,
  matcher)`. AssertJ: `assertThat(actual)...`. JUnit: `assertEquals(expected,
  actual)`. Mixing Hamcrest and AssertJ `assertThat` imports in one test is a
  foot-gun — and because Spring MockMvc's `ResultMatchers` are Hamcrest-based, a
  MockMvc test already has Hamcrest in scope whether you meant it or not. Be
  deliberate: read Hamcrest, write AssertJ.
- **JSONAssert strictness is the whole game.** The `boolean strict` / `JSONCompareMode`
  decides whether extra fields and array ordering fail the test. Default to **lenient**
  so tests aren't brittle; go strict only to pin exact structure/order.
- **REST Assured uses Groovy GPath, not Jayway JsonPath.** `[0].orders.size()` and
  closures like `find{...}` — not `$..orders`. Don't copy Jayway expressions into it.

## Mocking pitfalls

- **`UnnecessaryStubbingException`** fires when a stubbed call is never used — it's a
  feature (dead stub = unclear test). Fix the stub, or drop to `Strictness.LENIENT`
  deliberately, not reflexively.
- **The "add `mockito-inline` for final classes" advice is stale.** Since **Mockito 5**
  the inline mock-maker is the default in `mockito-core`; final classes, static methods
  and constructors mock out of the box, and the separate artifact stopped being
  published after 5.2. If you find that advice in an older answer or blog post, it
  describes Mockito 4.
- **Mocking what you don't own** turns a unit test into a guess about someone else's
  API. For an outbound HTTP dependency the honest tool is **WireMock** (real protocol,
  real serialization); for a real datastore it's **Testcontainers**.

## Infrastructure pitfalls

- **Testcontainers readiness ≠ container started.** Always set an explicit wait
  strategy (`Wait.forHttp(path).forStatusCode(200)`, `Wait.forLogMessage(regex, n)`),
  or tests race the service. This is the single most common cause of "passes locally,
  flaky in CI". Align module versions with the Testcontainers BOM.
- **Don't hand-map container ports and URLs on Spring Boot 3.1+.** `@ServiceConnection`
  derives the connection properties from the container, so the test can't drift out of
  sync with the image you're running.
- **Reach for a real container over an in-memory substitute** when behaviour differs —
  an embedded database that accepts SQL your production engine rejects will pass tests
  and fail in production.

## Browser tie-breaker (Playwright vs Selenium)

- **Playwright for new suites.** Its locators auto-wait until an element is actionable,
  which removes the explicit-wait boilerplate behind most Selenium flakiness. Published
  comparisons put it meaningfully faster with a far lower flake rate, and `trace.zip`
  turns a CI failure into a replayable timeline.
- **Selenium when you already have one.** A large, stable Selenium suite plus team
  fluency beats a rewrite. Add new specs in Playwright and let the old suite age out;
  a big-bang migration trades a known-good suite for an unknown one.

## BDD pitfall (Cucumber)

- **The selection criterion is social, not technical.** Cucumber earns its keep only
  when non-engineers genuinely read and write the feature files. When they don't, the
  Gherkin layer is indirection with no audience — plain JUnit + AssertJ expresses the
  same behaviour with fewer moving parts and no step-definition regex to maintain.
- **Run 7.x through the JUnit 5 Platform Suite** (`@Suite` +
  `@IncludeEngines("cucumber")`), not the legacy JUnit 4 runner.

## Async pitfall

- **`Thread.sleep` in async tests is always wrong** — it's slow *and* flaky. Use
  **Awaitility**: `await().atMost(...).until(...)` or `.untilAsserted(...)`. Use
  `ignoreExceptions()` while the resource is still coming up.

## Test-quality pitfall

- **Line/branch coverage does not measure whether tests assert anything.** A test can
  execute code and verify nothing. **PIT mutation testing** is the real signal: if a
  mutant survives, some test ran the code but didn't check the result. Run PIT on
  changed code (scoped) to keep it fast; triage equivalent mutants separately.

## Architecture pitfall

- **Non-deterministic `now()`.** Tests that call `LocalDate.now()`/`Instant.now()`
  without an injected `Clock` are time-flaky. Enforce it with an **ArchUnit** rule so
  the whole codebase stays testable, not just the file you're editing.

## Kotlin pitfalls (beyond the book)

These are **additions beyond Philip Riecks' (Java-framed) book**. For the mixed
source-set traps — `@JvmStatic`, platform types, `internal` friend-paths — see
`references/kotlin.md`.

- **Choose a mocker per type, not per module.** MockK earns its place for `object`s,
  extension/top-level functions, and suspending answers that need real control;
  Mockito + `mockito-kotlin` covers the rest (final classes mock by default since
  Mockito 5 — see Mocking pitfalls — and `onBlocking { }` stubs `suspend` functions).
  In a mixed source set both may sit on the classpath: an accepted cost, not an error.
  The actual mistake is **two mockers on the same type**, which produces confusing
  failures.
- **Coroutine tests must not use real time.** Use `runTest { }` (virtual time) with an
  injected `TestDispatcher` — not `runBlocking` + real `delay`, and never
  `Thread.sleep`. Production code must **take its dispatcher as a parameter**; a
  hardcoded `Dispatchers.IO`/`Main` can't be replaced, so the test can't control
  scheduling. Choose `StandardTestDispatcher` (manual `advanceUntilIdle()`) over
  `UnconfinedTestDispatcher` (eager) deliberately, not by copy-paste.
- **Don't use `runTest` to wait on real infrastructure.** Virtual time skips `delay()`;
  it cannot wait for a Testcontainers service, an HTTP endpoint, or a message to land
  on a broker — that is still **Awaitility**, in Kotlin exactly as in Java. Conversely,
  blocking inside `runTest` to bridge the gap stalls the virtual clock, so the test
  hangs or quietly takes real time. Coroutine scheduling and eventual consistency are
  different problems with different tools.
- **`Flow` tests silently pass without Turbine.** Collecting to a list and asserting on
  size can miss extra or late emissions. **Turbine**'s `test { }` fails on any
  unconsumed item, so over-emission is caught rather than averaged away.
- **PIT reports mislead on Kotlin.** The compiler emits `Intrinsics` null checks that
  PIT mutates, filling reports with `removed call to
  kotlin/jvm/internal/Intrinsics::… → SURVIVED` false positives. The option that
  suppresses them also stops mutating any statement containing a null check —
  including real business logic. Mutation scores are therefore **not comparable**
  between the Java and Kotlin halves of one module; read them accordingly.
- **Data classes change what you assert.** `equals`/`hashCode` are generated, so assert
  whole-object equality (AssertJ `isEqualTo`, or `shouldBe`) instead of field-by-field
  — but `copy()` is shallow, so deeply nested structures still need care.
