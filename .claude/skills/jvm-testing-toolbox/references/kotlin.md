# Kotlin testing — depth notes

**Last verified: 2026-07.** Version-sensitive claims follow the Currency rule in
`SKILL.md`. These tools are **beyond Philip Riecks' (Java-framed) book** — added
because real JVM projects mix Java and Kotlin, frequently in one source set.

Load this once routing has landed on a Kotlin-specific tool, **or when Java and
Kotlin tests in the same module interfere with each other** (last section). For the
quick decision, use the "Kotlin on the JVM" table in `SKILL.md`.

## MockK vs Mockito (+ mockito-kotlin)

- **Mockito is more capable on Kotlin than its reputation suggests.** Final-by-default
  Kotlin classes mock with no extra dependency — the inline mock-maker has been the
  default since Mockito 5 (see the Mockito card in `tool-cards.md`). What Kotlin adds
  on top is `mockito-kotlin`: `whenever`, `mock<T>()`, `argumentCaptor`, nullable-safe
  matchers (its `any()` won't push `null` into a non-null parameter), and
  `onBlocking { }` for stubbing `suspend` functions.
- **MockK earns its place** where Mockito genuinely can't be idiomatic: `object`
  singletons (`mockkObject`), top-level and extension functions (`mockkStatic`),
  and *suspending* answers needing real control (`coEvery { } coAnswers { … }`) —
  `onBlocking` handles simple returns but gets awkward with delays, indefinite
  suspension, and value-class boxing. `relaxed = true` / `@RelaxedMockK` returns
  sensible defaults; use a strict mock when unstubbed calls should fail.
- **The rule is one mocker per *type*, not per module.** Two mockers on the same
  type causes confusing failures. Two mockers in the same *module* — Mockito in the
  Java tests, MockK in the Kotlin ones — is a normal state for a mixed source set.
  It costs a second mental model; pay that deliberately rather than by accident.
- **When to stay on Mockito:** a mostly-Java module where a few tests happen to be
  Kotlin, or heavy Spring `@MockitoBean` integration. **Reach for MockK** in
  Kotlin-first or coroutine-heavy code.

## Coroutine testing: kotlinx-coroutines-test

- `runTest { }` installs a **virtual-time** scheduler: `delay()` is skipped, so a
  test of a 30-second timeout runs instantly and deterministically.
- **Dispatcher choice:**
  - `StandardTestDispatcher` — new coroutines are **queued**, not run, until you
    advance the scheduler (`advanceUntilIdle()`, `advanceTimeBy(ms)`,
    `runCurrent()`). Best when you want to assert intermediate states.
  - `UnconfinedTestDispatcher` — new coroutines start **eagerly** and run until
    their first suspension. Best for simple "fire and assert the result" tests.
- **Design for testability:** production code must take its `CoroutineDispatcher`
  as a constructor/parameter (or use an injected scope). A hardcoded
  `Dispatchers.IO`/`Dispatchers.Main` can't be replaced with a `TestDispatcher`,
  so scheduling can't be controlled. For `Dispatchers.Main` in unit tests, set
  `Dispatchers.setMain(testDispatcher)` in setup and `Dispatchers.resetMain()` in
  teardown.
- **Virtual time is not a waiting mechanism.** `runTest` can skip a `delay()` your
  own code issues; it cannot wait for a Testcontainers service, an HTTP endpoint, or
  a message to land on a broker. Those stay **Awaitility**, in Kotlin as in Java.
  Blocking inside `runTest` to bridge the gap stalls the virtual clock — the test
  hangs or silently takes real time.

## Flow testing — no extra library needed

`kotlinx-coroutines-test` covers this. The split that matters is cold vs hot.

- **Cold, finite flow:** collect it inside `runTest` — `toList()`, `first()`,
  `last()`. Exact, and what the official coroutines docs reach for. Assert on the
  contents, not just the size: a size-only assertion passes despite extra emissions.
- **Hot flow (`StateFlow`/`SharedFlow`) can't be `toList()`-ed.** It never completes,
  so the collection never returns and the test hangs — presenting as a slow test
  rather than a broken one. Collect it in `TestScope.backgroundScope.launch { … }`
  instead: coroutines started there are cancelled at the end of the test, so
  `runTest` doesn't wait forever. Pair it with `UnconfinedTestDispatcher` so the
  collector is live before the first emission.
- **Asserting between emissions** — drive the scheduler (`advanceUntilIdle()`,
  `runCurrent()`) between assertions rather than collecting everything up front.
- Combine with virtual time when the flow uses `delay`/`debounce` — `runTest`
  already provides it, so a `debounce(30.seconds)` test runs instantly.

A dedicated Flow-testing library (Turbine is the well-known one) buys ergonomics on
top of this — notably failing on unconsumed emissions — but it is not required, and
this skill doesn't route you to a dependency the platform already covers.

## Mixed source set: Java and Kotlin in one module

These bite only when both languages compile into the same source set — the case this
skill treats as primary.

- **`@BeforeAll` / `@AfterAll` / `@MethodSource` need `@JvmStatic`.** JUnit requires
  them to be static; Kotlin has no `static`, so they belong in a `companion object`
  marked `@JvmStatic`. The alternative is annotating the class
  `@TestInstance(Lifecycle.PER_CLASS)`, which removes the static requirement — usually
  cleaner in Kotlin, but it shares one instance across every test in the class, so
  mutable state now leaks between them.
- **Platform types quietly weaken null assertions.** A Java method returning `String`
  appears to Kotlin as `String!` — nullability unknown — so the compiler neither forces
  a check nor flags a redundant one. Assertions against Java-returned values can look
  null-safe while proving nothing. Annotate the Java side (JSpecify / `@Nullable`) or
  assert explicitly.
- **`internal` and test friend-paths.** Kotlin `internal` compiles to `public` with a
  mangled name, so same-module Java test code can reach it. Kotlin test code can too —
  but only because the build marks the test compilation a *friend* of main. The Gradle
  Kotlin plugin does this for the standard `test` source set; a custom source set
  won't get it automatically, and `internal` members will look mysteriously
  inaccessible.
- **JUnit 6 runs `suspend` test functions natively** (Java 17+ / Kotlin 2.2+), so the
  test method needs no `runBlocking` wrapper. You still want `runTest` for virtual time.
- **Backtick test names are JVM-legal but not portable.** Fine on the JVM; some tooling
  (and Android) rejects the characters. `@DisplayName` is the portable equivalent and
  reads the same from both languages.
- **Mutation scores aren't comparable across the two languages** in one module — see
  the PIT bullet in `pitfalls.md`.
