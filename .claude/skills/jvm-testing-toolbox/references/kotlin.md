# Kotlin testing — depth notes

**Last verified: 2026-07.** Version-sensitive claims follow the Currency rule in
`SKILL.md`. These tools are **beyond Philip Riecks' (Java-framed) book** — added
because real JVM projects mix Java and Kotlin, frequently in one source set.

Load this once routing has landed on a Kotlin-specific tool, **or when Java and
Kotlin tests in the same module interfere with each other** (last section). For the
quick decision, use the "Kotlin on the JVM" table in `SKILL.md`.

## MockK vs Mockito (+ mockito-kotlin)

- **Mockito is more capable on Kotlin than its reputation suggests.** Since
  **Mockito 5** the inline mock-maker is the default in `mockito-core`, so
  final-by-default Kotlin classes mock with **no extra dependency and no
  `mock-maker-inline` resource file**. `mockito-kotlin` adds `whenever`,
  `mock<T>()`, `argumentCaptor`, nullable-safe matchers (its `any()` won't push
  `null` into a non-null parameter), and `onBlocking { }` for stubbing `suspend`
  functions.
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

## Flow testing: Turbine

- `flow.test { … }` collects the flow inside a scope and **requires every emission
  to be consumed** — `awaitItem()`, `awaitComplete()`, `awaitError()`. If the flow
  emits more than the test consumes, the block fails; a plain `toList()` collect
  would silently pass.
- For infinite/hot flows, end with `cancelAndIgnoreRemainingEvents()`.
- Combine with virtual time (`runTest`) when the flow uses `delay`/`debounce`.

## Property testing: Kotest Property

- **`kotest-property` is a plain library, and that is the whole point.**
  `checkAll { a, b -> … }` runs inside an ordinary Jupiter `@Test` — no Kotest
  engine, no spec styles — so the module keeps a single test engine.
- It shrinks a failure to a minimal counterexample, which is what makes property
  testing worth more than hand-rolled random input.
- `kotest-assertions-core` is separable the same way (`shouldBe`, `shouldThrow`) if
  you want Kotlin-idiomatic assertions without adopting the Kotest engine.
- **No Java-side equivalent is recommended.** jqwik is the obvious candidate and is
  deliberately excluded: it registers its own Platform engine, is in pure
  maintenance mode, and carries an Anti-AI Usage Clause from v1.10. If Java-side
  invariants genuinely need property testing, make that a considered exception —
  not a default this skill routes you into.

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
