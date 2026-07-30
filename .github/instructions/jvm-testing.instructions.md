---
applyTo: "**/src/test/**,**/*Test.java,**/*Test.kt,**/*Tests.java,**/*Tests.kt,**/*IT.java,**/*IT.kt"
---
# JVM testing — tool selection

Scoped to test sources, so it only loads when you are actually writing tests.

**Canonical content is `.claude/skills/jvm-testing-toolbox/`** — `SKILL.md` for the
routing tables, `references/tool-cards.md` for per-tool notes,
`references/pitfalls.md` for cross-cutting traps, `references/kotlin.md` for Kotlin
depth and Java/Kotlin interop. Open those for the tie-breakers; this file is an index.

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

## Traps worth knowing before you write the test

- **Don't mix JUnit 4 and Jupiter** annotations/imports in one class — lifecycle
  callbacks stop firing and tests "pass" without running. Easy to do by accident with
  Spring Boot on the classpath.
- **Don't mix JUnit 5.x and 6.x artifacts**; import the `junit-bom`.
- **Testcontainers: always set a wait strategy.** "Container started" ≠ "service
  ready", and that race is the top cause of passes-locally-flaky-in-CI. On Spring Boot
  3.1+ use `@ServiceConnection` instead of hand-mapping ports.
- **Never `Thread.sleep`.** Awaitility for wall-clock waiting; `runTest` for coroutine
  scheduling. Virtual time cannot wait on a container, and blocking inside `runTest`
  stalls the virtual clock.
- **Never two mockers on the same type.** Mockito 5 already mocks final classes — the
  "add `mockito-inline`" advice is stale. Reach for MockK only for Kotlin `object`s,
  extension functions, or suspending answers.
- **Line coverage doesn't measure whether tests assert anything.** PIT's mutation
  score does.

If the answer isn't in `SKILL.md`, say so rather than reaching for a tool that isn't
listed — the list is deliberately curated, and `README.md` records what was cut.
