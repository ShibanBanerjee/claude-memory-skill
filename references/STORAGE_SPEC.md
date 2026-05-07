# Storage Field Specifications

## The Core Principle
Do not compress. Do not summarise at the expense of detail.
A few hundred extra words costs nothing. A lost decision costs everything.

## Field Specifications

### summary (TEXT, required)
**Target length:** 1,500–4,000 words
**Structure:** Flowing prose organised by topic. Not bullet points.
**Must include:**
- Every significant idea discussed, even if not conclusively resolved
- The reasoning behind every decision, not just the outcome
- What was rejected and precisely why
- Any frameworks or mental models applied
- The sequence of the conversation — what led to what
- Specific numbers, names, product details (not vague references)
- Any instructions the user gave about how Claude should behave
- The current state at the end of the conversation — where things stand

**Anti-patterns:**
- "We discussed the product strategy" — too vague
- Bullet point lists instead of prose — loses connective reasoning
- Omitting rejected options — future Claude may re-propose them
- Rounding numbers — exact figures matter
- Generic placeholders — "the app" instead of the app's actual name

### key_decisions (JSONB array of strings)
**Format:** Each string = "[WHAT was decided] — [WHY] — [What was REJECTED and why]"
**Minimum:** 10 entries for any substantive conversation
**Good example:**
  "PostgreSQL chosen as primary datastore — evaluated CockroachDB and PlanetScale;
   Postgres wins on operational familiarity, extension ecosystem (pgvector),
   and cost at current scale; revisit if global multi-region becomes a requirement"
**Bad example:**
  "Decided to use curated images"

### open_questions (JSONB array of strings)
**Format:** Each string must be specific and actionable
**Good:** "Auth strategy for the notification service: it needs user data from
          the users module — options are pass data at call time, replicate a
          users read model, or use a shared token; tradeoffs in consistency
          vs coupling need to be resolved before the service boundary is final"
**Bad:** "Decide on temples"

### entities (JSONB object)
```json
{
  "people":    ["Full name (role)"],
  "products":  ["Product names"],
  "companies": ["Company names"],
  "frameworks": ["JTBD", "Hooked Model"],
  "documents": ["Filename.docx"],
  "tools":     ["Tool names"],
  "concepts":  ["Key concepts coined in this conversation"]
}
```

### tags (TEXT[])
5–12 lowercase hyphenated strings.
Include: project-name, domain, key-concepts, framework-names, app-names.
These are the words someone will search months later.

Stored as a PostgreSQL native array with a GIN index — searchable via `'tag' = ANY(tags)` in SQL or `tags=cs.{tag}` in PostgREST.

### token_count_est (INTEGER)
Word count of the summary field, used as a rough proxy for token count.
Set automatically by mem.py using `len(summary.split())`.
Claude sets this to the actual word count when using MCP mode.
