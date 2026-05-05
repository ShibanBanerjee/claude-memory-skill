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

### instructions (JSONB array of strings)
Capture anything the user told Claude to always/never do.
Examples:
- "Always format responses in markdown suitable for Word/Google Docs"
- "Default to 9:16 vertical format for all video prompts"
- "Never suggest tokenisation as a creator incentive model"

### entities (JSONB object)
```json
{
  "people":    ["Full name (role)"],
  "products":  ["Product names"],
  "companies": ["Company names"],
  "frameworks": ["JTBD", "Hooked Model", etc],
  "documents": ["Filename.docx"],
  "tools":     ["Tool names"],
  "concepts":  ["Key concepts coined in this conversation"]
}
```

### tags (TEXT array)
5–12 lowercase hyphenated strings.
Include: project-name, domain, key-concepts, framework-names, app-names.
These are the words someone will search months later.
