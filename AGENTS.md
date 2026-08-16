# AGENTS.md

This repo packages one agent skill: a **curated router for JVM testing tool selection**,
covering Java and Kotlin in the same module.

**When a testing-tool question comes up, read
`.claude/skills/jvm-testing-toolbox/SKILL.md`** — it maps problem to tool and, more
usefully, carries the tie-breakers between overlapping tools. Once routing has landed,
`references/tool-cards.md` has one high-signal note per tool, `references/pitfalls.md`
the cross-cutting traps, and `references/kotlin.md` Kotlin depth plus Java/Kotlin
interop in a shared source set.

The tool list is deliberately not duplicated here. A copy would drift from the router
the first time a tool is added or dropped, and a stale index is worse than none.

## Always true

- **Don't mix JUnit 4 and Jupiter** annotations/imports in one test class — lifecycle
  callbacks stop firing and tests "pass" without running.
- **Don't mix JUnit 5.x and 6.x artifacts** on one classpath; import the `junit-bom`.
- **Never two mockers on the same type.** Mockito and MockK may coexist in a mixed
  Java/Kotlin module, but not on one type.
- **`Thread.sleep` is never the answer.** Awaitility for wall-clock waiting, `runTest`
  for coroutine scheduling — virtual time cannot wait on a container.
- **One engine.** JUnit Jupiter runs both languages; nothing needing a second JUnit
  Platform engine belongs here.

If the answer isn't in `SKILL.md`, that is information — the list is curated, and
`README.md` records what was cut and why. Say so rather than reaching for something
off-map.
