# Digital Shield — Coding Agent Guide

## Purpose

Use this file when working with Codex or another coding assistant.

The goal is to keep changes small, understandable, and easy to test.

---

# 1. Core Rule

Give the coding agent only **1–3 related features or changes per prompt**.

Do not ask it to build the entire project in one request.

Bad:

```text
Build the backend, both frontends, agent, claim verifier,
vision, Urdu, TTS, tests, and deployment.
```

Good:

```text
Create the FastAPI skeleton, health endpoint,
and request/response schemas.
Do not implement verification logic yet.
```

---

# 2. Required Context

Before major coding work, the agent should read:

1. `docs/project_context.md`
2. `docs/architecture.md`
3. Relevant existing source files
4. `docs/development_plan.md` when planning next milestone

For bug fixes, also inspect:

- relevant tests
- current API schema
- recent affected files

---

# 3. Architecture Rules

Do not violate these without explicit approval:

- One shared backend
- Two separate frontends
- Same API contract
- Verification logic belongs in backend
- One verification agent
- Tools remain separate and focused
- No unnecessary database
- No authentication for MVP
- No real WhatsApp integration for MVP
- Free tools/resources only
- English + Urdu for MVP

---

# 4. Code Style

- Keep code straightforward.
- Avoid unnecessary abstractions.
- Avoid adding dependencies unless needed.
- Keep comments short and useful.
- Prefer comments only where logic is not obvious.
- Do not leave large explanatory comment blocks in normal code.
- Preserve existing naming conventions.

---

# 5. Change Discipline

Before editing:

1. Inspect relevant files.
2. State what will change.
3. Avoid unrelated refactors.

After editing:

1. Summarize changed files.
2. Explain behavior changes briefly.
3. Run relevant tests.
4. Report failures honestly.
5. Do not claim tests passed unless they were actually run.

---

# 6. Documentation Discipline

Update `project_context.md` when:

- Architecture changes
- A milestone is completed
- API contract changes
- New tools are added
- Important constraints change
- Known limitations change

Do not rewrite stable docs unnecessarily.

---

# 7. Commit Messages

Commit messages must reflect all substantive changes.

Examples:

```text
feat: add FastAPI verification endpoint and schemas
```

```text
feat: add URL checker and agent tool routing
```

```text
feat: connect browser frontend to verification API
```

```text
fix: preserve follow-up state across verification requests
```

Avoid vague commits such as:

```text
update files
changes
docs
```

when the commit contains code changes too.

---

# 8. Testing Expectations

Each feature should have a manual or automated verification path.

Examples:

Backend:

- Swagger
- pytest
- direct API request

Frontend:

- local run
- known test input
- error state
- responsive layout where relevant

Agent/tool work:

- test expected tool selection
- test no unnecessary tool use
- test ambiguous input
- test structured output

---

# 9. Prompt Template for Coding Agents

```text
Read:
- docs/project_context.md
- docs/architecture.md
- the relevant existing source files

Task:
[1–3 related changes only]

Requirements:
- Preserve the current architecture.
- Keep verification logic in the backend.
- Do not add unrelated features.
- Use only free dependencies/resources.
- Keep code simple and comments concise.
- Run the relevant tests after implementation.

At the end, report:
1. files changed
2. what was implemented
3. tests run and results
4. any remaining limitation

Do not create a commit unless I explicitly ask.
```

---

# 10. Review Questions

Before accepting a coding-agent change, check:

- Did it modify unrelated files?
- Did it duplicate backend logic in a frontend?
- Did it change the API contract?
- Did it add a dependency we do not need?
- Did it introduce paid infrastructure?
- Did it overcomplicate the solution?
- Did it actually test the changed behavior?
- Does it preserve both frontend channels?
