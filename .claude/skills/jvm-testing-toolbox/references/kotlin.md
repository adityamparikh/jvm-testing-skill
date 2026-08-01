# Kotlin testing — depth notes

**Last verified: 2026-07.** Version-sensitive claims follow the Currency rule in
`SKILL.md`. Tool routing lives in the **Kotlin on the JVM** table there; load this
file when Java and Kotlin tests in the same module interfere with each other.

## Flow testing — no extra library needed

`kotlinx-coroutines-test` covers this.

A dedicated Flow-testing library (Turbine is the well-known one) buys ergonomics on
top of this — notably failing on unconsumed emissions — but it is not required, and
this skill doesn't route you to a dependency the platform already covers.

## Mixed source set: Java and Kotlin in one module

Bites only when both languages compile into the same source set — the case this skill
treats as primary.

- **`@BeforeAll` / `@AfterAll` / `@MethodSource` need `@JvmStatic`** in a `companion
  object`. Alternative: `@TestInstance(Lifecycle.PER_CLASS)` on the class — removes the
  static requirement, but one instance is shared across every test in the class, so
  mutable state now leaks between them.
- **Platform types quietly weaken null assertions.** A Java method returning `String`
  is `String!` to Kotlin — nullability unknown — so the compiler neither forces a check
  nor flags a redundant one. Assertions on Java-returned values can look null-safe
  while proving nothing. Annotate the Java side (JSpecify / `@Nullable`) or assert
  explicitly.
- **`internal` needs a friend-path outside the standard `test` source set.** `internal`
  compiles to `public` with a mangled name, so same-module Java test code reaches it;
  Kotlin test code reaches it only because the build marks the test compilation a
  *friend* of main. The Gradle Kotlin plugin wires that for `test` only — in a custom
  source set, `internal` members look mysteriously inaccessible.
- **Backtick test names are JVM-legal but not portable.** Some tooling (and Android)
  rejects the characters; `@DisplayName` is the portable equivalent and reads the same
  from both languages.
- **PIT mutation scores aren't comparable across the two languages** in one module.
  Kotlin's generated `Intrinsics` null checks add mutants Java code never has, so the
  Kotlin figure reads artificially low. Compare each language against itself.
