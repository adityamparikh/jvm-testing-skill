# Redundancy audit — jvm-testing-toolbox

Subject `claude-opus-5` with no skill loaded, 3 runs per probe, 31 claims, $6.21.

`R_asked` = knows the fact when asked directly. `R_task` = reaches for it unprompted in a realistic scenario. The gap between them is what a checklist buys.

**Overall (knowledge claims, n=27): R_asked 0.84, R_task 0.80, gap +0.04 -> CUT**

## By file

| File | n | R_asked | R_task | Gap | Verdict |
|---|---|---|---|---|---|
| `references/tool-cards.md` | 7 | #######... 0.74 | ######.... 0.62 | +0.12 | **TRIM** |
| `references/kotlin.md` | 6 | ########.. 0.83 | ########.. 0.75 | +0.08 | **CUT** |
| `SKILL.md` | 7 | #########. 0.88 | #########. 0.88 | +0.00 | **CUT** |
| `references/pitfalls.md` | 7 | #########. 0.91 | #########. 0.93 | -0.02 | **CUT** |

## By section

| File | Section | n | R_asked | R_task | Verdict |
|---|---|---|---|---|---|
| `references/tool-cards.md` | ## Test frameworks | 1 | 0.33 | 0.83 | **KEEP** |
| `references/tool-cards.md` | ## Kotlin (beyond the book) | 1 | 0.33 | 0.00 | **KEEP** |
| `SKILL.md` | ### Real infrastructure (integration / e2e) | 1 | 0.50 | 0.50 | **TRIM** |
| `references/kotlin.md` | ## Mixed source set: Java and Kotlin in one module | 1 | 0.50 | 0.50 | **TRIM** |
| `references/tool-cards.md` | ## Architecture & quality | 1 | 0.50 | 1.00 | **TRIM** |
| `references/pitfalls.md` | ## Assertion pitfalls | 1 | 0.67 | 1.00 | **TRIM** |
| `references/pitfalls.md` | ## Mocking pitfalls | 1 | 0.67 | 1.00 | **TRIM** |
| `SKILL.md` | ### Test frameworks | 1 | 0.83 | 0.67 | **CUT** |
| `SKILL.md` | ### Behaviour-driven testing | 1 | 0.83 | 1.00 | **CUT** |
| `references/kotlin.md` | ## MockK vs Mockito (+ mockito-kotlin) | 2 | 0.83 | 0.75 | **CUT** |
| `references/kotlin.md` | ## Coroutine testing: kotlinx-coroutines-test | 2 | 0.92 | 0.75 | **CUT** |
| `SKILL.md` | ### Assertion libraries | 1 | 1.00 | 1.00 | **CUT** |
| `SKILL.md` | ### REST API testing | 1 | 1.00 | 1.00 | **CUT** |
| `SKILL.md` | ### Mocking & stubbing | 1 | 1.00 | 1.00 | **CUT** |
| `SKILL.md` | ### Kotlin on the JVM | 1 | 1.00 | 1.00 | **CUT** |
| `references/kotlin.md` | ## Flow testing — no extra library needed | 1 | 1.00 | 1.00 | **CUT** |
| `references/pitfalls.md` | ## Framework pitfalls | 1 | 1.00 | 1.00 | **CUT** |
| `references/pitfalls.md` | ## JUnit 6 migration pitfalls | 1 | 1.00 | 0.67 | **CUT** |
| `references/pitfalls.md` | ## Infrastructure pitfalls | 1 | 1.00 | 1.00 | **CUT** |
| `references/pitfalls.md` | ## BDD pitfall (Cucumber) | 1 | 1.00 | 1.00 | **CUT** |
| `references/pitfalls.md` | ## Kotlin pitfalls (beyond the book) | 1 | 1.00 | 0.83 | **CUT** |
| `references/tool-cards.md` | ## Assertion libraries | 1 | 1.00 | 0.00 | **COMPRESS** |
| `references/tool-cards.md` | ## Mocking | 1 | 1.00 | 1.00 | **CUT** |
| `references/tool-cards.md` | ## Real infrastructure | 1 | 1.00 | 0.50 | **COMPRESS** |
| `references/tool-cards.md` | ## REST API | 1 | 1.00 | 1.00 | **CUT** |

## Highest-value claims (model least likely to know)

These are the skill's real payload. Task-eval assertions should be drawn from here —
an assertion the base model already satisfies measures nothing.

- **0.33/0.00** `references/tool-cards.md` — MockK is warranted over Mockito for Kotlin object singletons (mockkObject), top-level/extension functions (mockkStatic) and suspending answers (coEvery/coAnswers) — not merely to mock final classes — and in a mixed module the rule is never two mockers on the same type, not one mocker per module.
- **0.33/0.83** `references/tool-cards.md` — JUnit 6 requires Java 17+, so projects on Java 8–16 must stay on JUnit 5 (which shares the same Jupiter API/packages), and reaching 5.14 first surfaces 6.0 removals as deprecations.
- **0.50/0.50** `SKILL.md` — Testcontainers tests must always set an explicit wait strategy, because "container started" ≠ "service ready" and that race is the top cause of flaky integration tests.
- **0.50/0.50** `references/kotlin.md` — JUnit 6 runs suspend test functions natively — requiring Java 17+ and Kotlin 2.2+ — so no runBlocking wrapper is needed, though runTest is still wanted for virtual time.
- **0.50/1.00** `references/tool-cards.md` — ArchUnit analyses bytecode, so the same architecture rules apply to Java and Kotlin alike (and it runs as a JUnit test).
- **0.67/0.50** `references/kotlin.md` — The constraint is one mocking framework per type, not per module — Mockito in Java tests and MockK in Kotlin tests within the same module is a normal, acceptable state.
- **0.67/1.00** `references/pitfalls.md` — REST Assured path expressions use Groovy GPath (e.g. `[0].orders.size()`, `find{...}`), not Jayway JsonPath syntax.
- **0.67/1.00** `references/pitfalls.md` — Since Mockito 5 the inline mock-maker is the default in mockito-core (final classes, statics, constructors mock out of the box) and the separate mockito-inline artifact stopped being published after 5.2.
- **0.83/0.50** `references/kotlin.md` — runTest's virtual time only skips delays your own code issues; waiting on external systems (Testcontainers, HTTP endpoints, brokers) still requires Awaitility, and blocking inside runTest stalls the virtual clock.
- **0.83/0.67** `SKILL.md` — JUnit 6 (GA September 2025) requires Java 17+ and Kotlin 2.2+, so projects on Java 8–16 must stay on JUnit 5 (Jupiter).

## Widest elicitation gaps (knows it, does not use it)

Content to compress into a checklist rather than delete: the model has the fact
but will not produce it unless prompted.

- **gap +1.00** (1.00 -> 0.00) `references/tool-cards.md` — JSONAssert's third boolean/JSONCompareMode argument decides comparison strictness — lenient allows extra fields and any array order, strict enforces exact fields plus array order — and lenient should be the default for non-brittle tests.
- **gap +0.50** (1.00 -> 0.50) `references/tool-cards.md` — Testcontainers tests must always declare an explicit wait strategy (e.g. Wait.forHttp(path).forStatusCode(200) or Wait.forLogMessage(regex, n)) because a container being up is not the service being ready — the single most common cause of flaky integration tests.
- **gap +0.33** (0.83 -> 0.50) `references/kotlin.md` — runTest's virtual time only skips delays your own code issues; waiting on external systems (Testcontainers, HTTP endpoints, brokers) still requires Awaitility, and blocking inside runTest stalls the virtual clock.
- **gap +0.33** (1.00 -> 0.67) `references/pitfalls.md` — JUnit 6 requires Java 17+ and Kotlin 2.2+; projects on Java 8–16 should stay on JUnit 5 and migrate the JDK first.
- **gap +0.33** (0.33 -> 0.00) `references/tool-cards.md` — MockK is warranted over Mockito for Kotlin object singletons (mockkObject), top-level/extension functions (mockkStatic) and suspending answers (coEvery/coAnswers) — not merely to mock final classes — and in a mixed module the rule is never two mockers on the same type, not one mocker per module.
- **gap +0.17** (0.83 -> 0.67) `SKILL.md` — JUnit 6 (GA September 2025) requires Java 17+ and Kotlin 2.2+, so projects on Java 8–16 must stay on JUnit 5 (Jupiter).
- **gap +0.17** (0.67 -> 0.50) `references/kotlin.md` — The constraint is one mocking framework per type, not per module — Mockito in Java tests and MockK in Kotlin tests within the same module is a normal, acceptable state.
- **gap +0.17** (1.00 -> 0.83) `references/pitfalls.md` — A hot flow (StateFlow/SharedFlow) must never be collected with `toList()` in `runTest` because it never completes; collect it in `TestScope.backgroundScope` with `UnconfinedTestDispatcher`.

## Dead weight (model knows it and already uses it)

- **1.00/1.00** `SKILL.md` — JSONAssert compares leniently by default; strict mode (`strictMode`/`JSONCompareMode`) is what enforces array ordering and forbids extra fields.
- **1.00/1.00** `SKILL.md` — REST Assured's `jsonPath()` uses Groovy GPath, not Jayway JsonPath, so Jayway `$..` expressions must not be copied into it.
- **1.00/1.00** `SKILL.md` — Since Mockito 5 the inline mock-maker is the default, so final classes and static methods — including Kotlin's final-by-default classes — mock with no extra dependency.
- **1.00/1.00** `SKILL.md` — A hot flow (StateFlow/SharedFlow) never completes so `toList()` hangs; collect it in `TestScope.backgroundScope` with `UnconfinedTestDispatcher` so the collector is live before the first emission.
- **0.83/1.00** `SKILL.md` — Cucumber 7.x should be run via the JUnit 5 Platform Suite (`@Suite` + `@IncludeEngines("cucumber")`), not the legacy JUnit 4 runner.
- **1.00/1.00** `references/kotlin.md` — Mocking final-by-default Kotlin classes with Mockito needs no extra dependency because the inline mock-maker has been the default since Mockito 5.
- **1.00/1.00** `references/kotlin.md` — StandardTestDispatcher queues newly launched coroutines until the scheduler is advanced (advanceUntilIdle/advanceTimeBy/runCurrent), while UnconfinedTestDispatcher starts them eagerly until their first suspension.
- **1.00/1.00** `references/kotlin.md` — A StateFlow/SharedFlow must not be collected with toList() inside runTest — it never completes, so the test hangs; collect it in TestScope.backgroundScope.launch paired with UnconfinedTestDispatcher instead.
- **1.00/1.00** `references/pitfalls.md` — JUnit Jupiter test classes and methods may be package-private, so the `public` modifier carried over from JUnit 4 habit should not be added.
- **1.00/1.00** `references/pitfalls.md` — On Spring Boot 3.1+, container connection properties should come from `@ServiceConnection` rather than hand-mapped ports and URLs.

## Curation claims (reported separately, never averaged in)

4 claims, R_asked 0.33. These encode this author's editorial
choices, which nobody can know from general knowledge. A low score here is
arithmetic, not evidence of value: it says the decision is private, not that
following it produces better outcomes. Only the task evals can show that.

## What the verdicts mean

- **CUT** — model knows it and uses it unprompted
- **COMPRESS** — model knows it but does not reach for it - keep the reminder, drop the prose
- **TRIM** — model is unreliable here - keep the specific claims, cut the surrounding prose
- **KEEP** — genuine payload - the model does not have this

This audit decides where to spend the expensive task evals, and breaks ties at
the end. It does not on its own justify deleting a section: framing can change
behaviour in ways a decomposition into claims does not capture.
