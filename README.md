# JVM Testing Toolbox — an AI agent skill

> **Renamed from `java-testing-toolbox`.** The skill now covers Kotlin too, for
> mixed Java+Kotlin projects; its directory and skill name are
> `jvm-testing-toolbox`.

An [agent skill](https://code.claude.com/docs/en/skills) that helps AI coding
tools (Claude Code, Cursor, Copilot, …) **pick the right JVM testing tool for a
given challenge in a Java and/or Kotlin project** — the right framework,
assertion library, mocking approach, or HTTP / infrastructure / browser / BDD /
architecture tool — with the selection tie-breakers and pitfalls that generic
model knowledge tends to miss.

It's a **router**, not a tutorial: it deliberately does *not* re-teach things an
LLM already knows (basic JUnit 5 / Mockito / AssertJ usage). Its value is the
**map** — "for problem X, tools Y and Z exist; pick Y because…".

## Credit

This skill **began as a distillation of [Philip Riecks](https://rieckpil.de/)'
book**, and his selection and categorization are still its backbone:

> **_Java Testing Toolbox: 30 Testing Tools and Libraries Every Java Developer
> Must Know_** — Philip Riecks

It has since diverged, so please don't read the whole of it as his work:

- **Curated.** Several of the book's tools were dropped and the list re-tiered
  around what JVM teams reach for most — see Coverage above for each cut and its
  reason.
- **Extended.** Playwright, Cucumber, and the entire Kotlin side (MockK,
  kotlinx-coroutines-test, and the Java/Kotlin interop
  notes) are additions the book doesn't cover — it is Java-framed.
- **Updated.** Version-sensitive guidance is re-checked against current release
  notes and corrected where the ecosystem moved — JUnit 6 as the default, and
  Mockito 5 making the inline mock-maker standard, among others.

The Java tool selection, the categorization, and the pitfalls distilled from the
book are Philip's. The cuts, the additions, and any errors in them are mine.
Please support the original work:

- 📘 Book: https://leanpub.com/java-testing-toolbox
- ✍️ Blog: https://rieckpil.de/
- 💻 Runnable example code: https://github.com/rieckpil/java-testing-ecosystem
- 🎓 Testing Spring Boot Applications Masterclass: https://rieckpil.de/testing-spring-boot-applications-masterclass/
- 🐦 https://x.com/rieckpil · https://www.linkedin.com/in/rieckpil/

This repository contains **no reproduction of the book's prose or source code** —
it is an original, condensed decision map that points back to Philip's material
for the depth and runnable examples. If you find it useful, buy the book.

Packaged and maintained by [Aditya Parikh (@adityamparikh)](https://github.com/adityamparikh).

## What's inside

```
.claude/skills/jvm-testing-toolbox/     ← canonical content
├── SKILL.md                 # the router: problem → tool decision tables
└── references/
    ├── tool-cards.md        # one card per tool: purpose + the one high-signal note
    ├── pitfalls.md          # cross-cutting gotchas + tie-breaker rationale
    └── kotlin.md            # Kotlin depth + Java/Kotlin interop in one source set

AGENTS.md                                        ← index + pointer (most agents)
.github/instructions/jvm-testing.instructions.md ← index + pointer (Copilot)
.cursor/rules/jvm-testing.mdc                    ← index + pointer (Cursor)
```

### Which agents this works with

The routing tables are written for **Claude Code's skill format**, which loads
`SKILL.md` only when a testing question matches its description and pulls
`references/*` only once routing lands. That progressive disclosure is the design —
it keeps 170 lines of tables out of context on unrelated work.

Other agents get **pointer files**, each using that agent's own gating so the content
isn't always-loaded:

| File | Read by | Gating |
|---|---|---|
| `AGENTS.md` | Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf, Zed, Devin, Jules, VS Code, Junie — and Claude Code | always loaded, so it stays short |
| `.github/instructions/jvm-testing.instructions.md` | GitHub Copilot | `applyTo` globs — test sources only |
| `.cursor/rules/jvm-testing.mdc` | Cursor | `globs` + `alwaysApply: false` — auto-attaches on test files |

**None of them restate the tool list.** A copy would drift from the router the first
time a tool is added or dropped, and a stale index is worse than no index — so the
routing tables live in exactly one place.

How each avoids duplicating them differs, because the mechanisms differ:

- **Cursor** supports `@filename` includes, so the rule is a genuine pointer: it
  `@`-references `SKILL.md` and the three reference files and states nothing itself.
- **Copilot** and **AGENTS.md** have no include mechanism, so they instruct the agent
  to read `SKILL.md` and carry only a handful of silent-failure traps — JUnit 4/Jupiter
  mixing, `junit-bom` alignment, two mockers on one type, `Thread.sleep`. Those are
  stable enough to survive tool-list churn, which the index is not.

**One caveat:** for Copilot and AGENTS.md, a pointer only works if the agent actually
opens the referenced file — weaker than Cursor's `@` includes or Claude's native
loading.

## Coverage

Deliberately small, in two groups.

**Already on your classpath** — everything `spring-boot-starter-test` pulls in.
You use these whether or not you choose them, so the skill is about using them
*correctly*, not about adopting them:

| Problem | Tool |
|---|---|
| Test framework | JUnit 6 / 5 / 4 |
| Fluent assertions | AssertJ |
| Matcher assertions (you meet it via MockMvc) | Hamcrest |
| Mocking | Mockito |
| Compare a whole JSON document | JSONassert |
| Extract a value from JSON | JsonPath |
| Asynchronous code | Awaitility |

**Reached for constantly** — not in the starter, but the standing answer to a
problem most JVM teams hit:

| Problem | Tool |
|---|---|
| Any dependency that ships as a container | Testcontainers |
| Mock an external HTTP API | WireMock |
| Black-box test a REST API | REST Assured |
| Browser / end-to-end | Playwright |
| Gherkin specs read by non-engineers | Cucumber |
| Architecture rules as tests | ArchUnit |
| Generate test data | Instancio |
| Judge test quality beyond coverage | PIT |

**If the module has Kotlin** — additions beyond the book, because real JVM
projects mix the two languages, often in one source set:

| Problem | Tool |
|---|---|
| Mock a Kotlin `object`, extension fn, or suspending answer | MockK |
| Test `suspend` functions / coroutine scheduling | kotlinx-coroutines-test |
| Assert on values a `Flow` emits | kotlinx-coroutines-test |
| Java/Kotlin interop in one source set | `references/kotlin.md` |

Two tools, because that is all a mixed module needs. The governing rule is **one
engine**: JUnit Jupiter runs both languages. Libraries may differ per file; engines
may not — no tool requiring a second JUnit Platform engine appears anywhere in the
skill, which is a deliberate constraint rather than an omission.

### What was cut, and why

A survey benefits from breadth; a router is diluted by it, because every extra
destination is one more confident wrong turn an agent can take. The skill tracks
the ecosystem where it has moved since the book — JUnit 6 (GA September 2025) is
the current default, Playwright and Cucumber are additions — and drops what no
longer earns a slot:

| Cut | Reason |
|---|---|
| JfrUnit | Effectively abandoned — last release December 2021, still `1.0.0.Alpha2`. |
| Diffblue Cover | Circular: this skill is read by AI coding agents, so routing an agent to an AI test generator is a no-op. The tool itself is fine and maintained. |
| Gatling, JMH, ApacheBench | Load testing and microbenchmarking are a separate discipline with their own decision tree. Out of scope rather than badly served. |
| Selenide, Selenium | Folded into the Playwright row as the "you already have a Selenium suite" tie-breaker. |
| MockWebServer | WireMock is the default; a second HTTP-stub option added choice without adding capability. |
| LocalStack, GreenMail, MicroShed Testing | Narrow answers to problems Testcontainers now covers generically — any image, any wait strategy. |
| TestNG, Spock | JUnit 5/6 absorbed the differentiators (`@ParameterizedTest`, parallel execution); Spock additionally requires adopting Groovy, which is a language decision, not a library one. |
| JGiven | Cucumber is the standard Gherkin answer; two BDD entries served neither well. |
| XMLUnit | XML-specific and narrow enough to look up when you actually need it. |
| Pact | Contract testing is a real practice, but it needs a broker and a deploy gate — an infrastructure commitment, not a library choice. |
| Turbine | `kotlinx-coroutines-test` already tests `Flow` — `toList()` inside `runTest` for cold flows, `TestScope.backgroundScope` for hot ones. Turbine adds ergonomics (notably failing on unconsumed emissions), not capability, and its centre of gravity is Android. |
| Kotest (incl. Kotest Property) | The spec styles need a second Platform engine, which the one-engine rule rules out. The property module avoids that, but property-based testing is rarer on the JVM than several practices already cut — and with jqwik excluded it would have been Kotlin-only, which is a worse answer than not raising the topic. |

None of this says these are bad tools. They are answers to questions this router
has chosen not to answer.

## Usage

**Claude Code:** drop the `.claude/skills/jvm-testing-toolbox/` directory into a
project (or a personal skills directory) so your agent can discover it. It loads
`SKILL.md` when a testing-tool-selection question arises, then pulls `references/*`
only once routing lands on a specific tool.

**Other agents:** copy the skill directory *plus* the pointer file for your tool —
`AGENTS.md`, `.github/instructions/jvm-testing.instructions.md`, or
`.cursor/rules/jvm-testing.mdc`. The pointers are useless without the skill directory
they reference.

## License

[Apache-2.0](./LICENSE). The Java core is credited to Philip Riecks (see
[Credit](#credit)); the curation, the additions, and the packaging are provided
under Apache-2.0.
