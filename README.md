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

The book's tools, grouped by problem:

| Category | Tools |
|---|---|
| Test frameworks | JUnit 6, JUnit 5, JUnit 4, TestNG, Spock |
| Assertion libraries | AssertJ, Hamcrest, JsonPath, JSONAssert, XMLUnit |
| Mocking | Mockito (+ Spock mocks) |
| HTTP mocking | WireMock, MockWebServer |
| Real infrastructure | Testcontainers, LocalStack, GreenMail, MicroShed Testing |
| Browser / UI | Selenide, Selenium |
| REST API | REST Assured |
| Async | Awaitility |
| Performance | Gatling, ApacheBench, JMH, JfrUnit |
| Behavior-driven | JGiven (+ Spock) |
| Contract testing | Pact |
| Architecture & quality | ArchUnit, Instancio, PIT mutation testing |

The skill tracks the ecosystem where it has moved since the book — e.g. JUnit 6
(GA September 2025) is covered as the current default, with its migration
pitfalls, on top of the book's JUnit 5 guidance.

It also **curates rather than mirrors** the book's list. A survey benefits from
breadth; a router is diluted by it, because every extra destination is another
confident wrong turn an agent can take. So:

- **Diffblue Cover is omitted.** This skill is read by AI coding agents — routing
  an AI agent to an AI test generator is circular. (The tool is fine and still
  maintained; it just has no job here.)
- **GreenMail and MicroShed Testing are marked _Conditional_** — reach for them only
  when that exact narrow problem is yours (you send mail; you run Jakarta EE /
  MicroProfile), never as a default or by analogy.

## Usage

Drop the `.claude/skills/java-testing-toolbox/` directory into a project (or a
personal skills directory) so your agent can discover it. The agent loads
`SKILL.md` when a testing-tool-selection question arises, then pulls
`references/*` only once routing lands on a specific tool.

## License

[Apache-2.0](./LICENSE). The knowledge is credited to Philip Riecks (see above);
the packaging is provided under Apache-2.0.
