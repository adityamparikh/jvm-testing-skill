---
applyTo: "**/src/test/**,**/*Test.java,**/*Test.kt,**/*Tests.java,**/*Tests.kt,**/*IT.java,**/*IT.kt"
---
# JVM testing — tool selection

Scoped to test sources, so it only loads when you are actually writing tests.

**Before choosing a testing tool, read `.claude/skills/jvm-testing-toolbox/SKILL.md`.**
It is a curated router: which tool fits which problem, and — the part that matters —
the tie-breakers between overlapping tools. Then, once routing has landed:

- `references/tool-cards.md` — one high-signal note per tool
- `references/pitfalls.md` — cross-cutting traps and tie-breaker rationale
- `references/kotlin.md` — Kotlin depth, and Java/Kotlin interop in one source set

The tool list is not restated here on purpose: a copy would drift from the router the
first time a tool is added or dropped. Read the file.

## Worth knowing before you write the test

These are stable enough to state twice — they are silent-failure traps, not tool choices.

- **Don't mix JUnit 4 and Jupiter** annotations or imports in one class. Lifecycle
  callbacks stop firing and tests "pass" without running — easy to do by accident with
  Spring Boot on the classpath.
- **Don't mix JUnit 5.x and 6.x artifacts**; import the `junit-bom`.
- **Testcontainers: always set a wait strategy.** "Container started" ≠ "service ready",
  and that race is the top cause of passes-locally-flaky-in-CI. On Spring Boot 3.1+ use
  `@ServiceConnection` rather than hand-mapping ports.
- **Never `Thread.sleep`.** Awaitility for wall-clock waiting; `runTest` for coroutine
  scheduling. They are not interchangeable — virtual time cannot wait on a container,
  and blocking inside `runTest` stalls the virtual clock.
- **Never two mockers on the same type.** Mockito 5 already mocks final classes, so the
  "add `mockito-inline`" advice is stale; reach for MockK only for Kotlin `object`s,
  extension functions, or suspending answers.
- **Line coverage doesn't measure whether tests assert anything.** PIT's mutation score
  does.
