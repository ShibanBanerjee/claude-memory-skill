# Workflow Example

## Scenario

You've spent two hours with Claude working through an architecture decision —
microservices vs monolith for a new backend. You've evaluated tradeoffs, made
a call, documented the reasoning, and identified three follow-up tasks. You
want to save all of this before closing the tab, and pick it up next week.

## Saving context

At the end of the session, type:

```
/mem Backend Architecture — Microservices Decision
```

Claude reads the full conversation, extracts the decision record, and stores it:

```
✅ Memory saved.

   ID:        a3f2c1d8-4e5b-4f6a-9c1d-2e3f4a5b6c7d
   Title:     Backend Architecture — Microservices Decision
   Project:   backend-rewrite
   Summary:   ~1,840 words
   Decisions: 6
   Questions: 3
   Tags:      architecture, microservices, postgres, api-design

Use /context backend architecture in any future conversation to restore this.
```

## Restoring context the following week

Open a new Claude conversation and type:

```
/context backend architecture decision
```

Claude retrieves the stored memory and responds:

```
📚 Memory loaded: "Backend Architecture — Microservices Decision"
Saved: 2026-05-05 | Project: backend-rewrite | ~1,840 words
6 decisions locked | 3 open questions

Context restored. You landed on a modular monolith for the initial launch,
with clear service boundaries that make extraction straightforward later.
The main reasons were operational simplicity and team size.

Open question: which shared database strategy to use if services are
extracted — schema-per-service vs shared schema with row-level isolation.

Where would you like to continue?
```

No re-explaining. No re-building context. Claude knows the full decision history,
the reasoning, and exactly where the open threads are.

## Updating a memory mid-project

If the decision changes or new context emerges, run:

```
/mem update
```

Claude reads the current conversation, finds the existing memory for this project,
and merges the new content in — updating the summary, resolving answered questions,
and appending new decisions. The original entry's ID stays the same.
