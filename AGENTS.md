# AGENTS.md

This repo packages one agent skill: a **router for JVM testing tool selection**,
covering Java and Kotlin in the same module.

**Canonical content lives in `.claude/skills/jvm-testing-toolbox/`** — `SKILL.md`
holds the routing tables, and `references/{tool-cards,pitfalls,kotlin}.md` hold the
per-tool notes, cross-cutting traps and Kotlin/interop depth. Read those when a
testing-tool question comes up; this file is only an index.

## Index — which tool for which problem

| Problem | Tool |
|---|---|
| Unit/integration test, Java 17+ | JUnit 6 (Jupiter) |
| Fluent assertions | AssertJ |
| Matcher assertions | Hamcrest — read it, don't write it (arrives via Spring MockMvc) |
| Mock a collaborator | Mockito |
| Compare a JSON document | JSONassert |
| Extract a value from JSON | JsonPath |
| Wait for something eventual | Awaitility |
| Any dependency that ships as a container | Testcontainers |
| Mock an external HTTP API | WireMock |
| Black-box test a REST API | REST Assured |
| Browser / end-to-end | Playwright |
| Gherkin specs non-engineers read | Cucumber |
| Architecture rules as tests | ArchUnit |
| Generate test data | Instancio |
| Judge test quality beyond coverage | PIT (pitest) |
| Kotlin: mock an `object`/extension fn/suspending answer | MockK |
| Kotlin: `suspend` functions, coroutine scheduling, `Flow` | kotlinx-coroutines-test |

The tie-breakers are the point, and they are **not** in this table — open `SKILL.md`
before committing to a choice.

## Always true

- **Don't mix JUnit 4 and Jupiter** annotations/imports in one test class. Lifecycle
  callbacks stop firing and tests "pass" without running.
- **Don't mix JUnit 5.x and 6.x artifacts** on one classpath — import the `junit-bom`.
- **Never two mockers on the same type.** Mockito and MockK may coexist in a mixed
  Java/Kotlin module, but not on one type.
- **`Thread.sleep` is never the answer.** Awaitility for wall-clock waiting, `runTest`
  for coroutine scheduling. They are not interchangeable — virtual time cannot wait
  on a container.
- **One engine.** JUnit Jupiter runs both languages; no tool needing a second JUnit
  Platform engine belongs here.

If the answer isn't in `SKILL.md`, that is information — say so rather than reaching
for something off-map.
