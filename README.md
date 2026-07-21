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

All 30 tools, the categorization, the selection guidance, and the pitfalls are
distilled from that book. Please support the original work:

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

The 30 tools from the book, grouped by problem:

| Category | Tools |
|---|---|
| Test frameworks | JUnit 5, JUnit 4, TestNG, Spock |
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
| Architecture & quality | ArchUnit, Instancio, Diffblue Cover, PIT mutation testing |

## Usage

Drop the `.claude/skills/java-testing-toolbox/` directory into a project (or a
personal skills directory) so your agent can discover it. The agent loads
`SKILL.md` when a testing-tool-selection question arises, then pulls
`references/*` only once routing lands on a specific tool.

## License

[Apache-2.0](./LICENSE). The knowledge is credited to Philip Riecks (see above);
the packaging is provided under Apache-2.0.
