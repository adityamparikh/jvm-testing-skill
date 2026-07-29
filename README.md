# Java Testing Toolbox — an AI agent skill

An [agent skill](https://code.claude.com/docs/en/skills) that helps AI coding
tools (Claude Code, Cursor, Copilot, …) **pick the right Java/JVM testing tool
for a given challenge** — the right framework, assertion library, mocking
approach, or HTTP / infrastructure / UI / performance / contract / architecture
tool — with the selection tie-breakers and pitfalls that generic model knowledge
tends to miss.

It's a **router**, not a tutorial: it deliberately does *not* re-teach things an
LLM already knows (basic JUnit 5 / Mockito / AssertJ usage). Its value is the
**map** — "for problem X, tools Y and Z exist; pick Y because…".

## Credit

This skill is **based entirely on the work of [Philip Riecks](https://rieckpil.de/)**
and his book:

> **_Java Testing Toolbox: 30 Testing Tools and Libraries Every Java Developer
> Must Know_** — Philip Riecks

The Java tool selection, the categorization, the selection guidance, and the
pitfalls are distilled from that book — **curated rather than mirrored** (see
Coverage above for what is omitted, marked conditional, and why). Please support
the original work:

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
.claude/skills/java-testing-toolbox/
├── SKILL.md                 # the router: problem → tool decision tables
└── references/
    ├── tool-cards.md        # one card per tool: purpose + the one high-signal note
    └── pitfalls.md          # cross-cutting gotchas + tie-breaker rationale
```

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

None of this says these are bad tools. They are answers to questions this router
has chosen not to answer.

## Usage

Drop the `.claude/skills/java-testing-toolbox/` directory into a project (or a
personal skills directory) so your agent can discover it. The agent loads
`SKILL.md` when a testing-tool-selection question arises, then pulls
`references/*` only once routing lands on a specific tool.

## License

[Apache-2.0](./LICENSE). The knowledge is credited to Philip Riecks (see above);
the packaging is provided under Apache-2.0.
