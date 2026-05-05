# Example: Retrieving a Memory

## Setup

User opens a new Claude conversation — a different session, possibly days later.
No context from the previous conversation exists.

## Command

```
/context backend architecture
```

## What Claude does

1. Runs a full-text search against `claude_memories` for "backend architecture"
2. Finds one matching entry saved from a previous session
3. Loads the full record: summary, decisions, open questions, instructions, entities
4. Confirms to the user and resumes

## Claude's response

```
📚 Memory loaded: "Backend Architecture — Microservices Decision"
Saved: 2026-05-05 | Project: backend-rewrite | ~1,840 words
6 decisions locked | 3 open questions | 2 instructions active

Context restored. You chose a modular monolith for the initial launch, with
explicit service boundaries designed for future extraction. The call was driven
by team size and operational overhead concerns. Three things were left open:
database isolation strategy, deployment pipeline design, and whether to
standardise on gRPC or REST for internal service calls.

Where would you like to pick up?
```

## Notes

- Claude treats all fields in the retrieved memory as fully known background
- It won't re-ask for information already captured in the summary
- Active `instructions` (e.g. formatting preferences) are applied automatically
- If multiple memories match the query, Claude shows a short list and asks which to load
