# Memory Compression Guide

## The Core Philosophy: Lossless, Not Minimal

Most AI memory systems compress aggressively — reducing hours of conversation to a paragraph. This destroys nuance, loses reasoning, and forces you to re-explain the "why" behind every decision.

`claude-memory-skill` takes the opposite approach: **store everything that matters, because the database can hold it.**

A typical memory entry is 1,500 to 4,000 words. That's a detailed project brief, not a tweet. It's small enough to be injected into any new conversation without burning significant tokens, and comprehensive enough that future Claude can truly pick up where you left off.

---

## What "Everything That Matters" Means

### Decisions WITH Reasoning
The most common failure mode of AI memory: capturing *what* was decided without capturing *why*.

**Bad capture:**
> "Decided to use PostgreSQL for the primary datastore."

**Good capture:**
> "PostgreSQL chosen over MongoDB for the content store — document model seemed appealing early on, but relational queries across user/content/engagement data were getting progressively more complex and inefficient. Postgres with JSONB gives flexibility where needed without sacrificing query power. Migration cost is real but worth it before the data volume grows further."

The good version tells future Claude: don't suggest AI images again, here's why, here's the condition under which it could be revisited.

---

### Rejected Ideas WITH Their Rejection Reasons

This is the most underrated thing to capture. When an idea is rejected in a conversation, it's usually rejected for good reasons. Without capturing the rejection, future Claude will re-propose the same idea and waste the user's time.

**Examples of what to capture:**
> "Redis chosen over Postgres for the session cache — Postgres latency at P99 was unacceptable for the login hot path; Redis gives sub-millisecond reads with acceptable durability tradeoffs for session data specifically."

> "Monolithic single-app architecture REJECTED — serves 7 different personas with different needs, UX becomes a compromise for everyone; viral loops are persona-specific; failed features drag the entire product. Constellation architecture chosen instead."

---

### Specific Numbers and Names

Numbers are meaningless without their context, but omitting them makes future context incomplete.

Capture:
- Revenue projections with their basis (₹305 Cr ARR Year 3, conservative, based on 2% premium conversion at ₹500/yr avg)
- User targets with their timeframes (50,000 DAU by Month 6, 5,000,000 DAU by Month 36)
- Market sizes that were referenced (₹3.5 lakh crore religion economy, ₹2.5 lakh crore pilgrimage market at 14% CAGR)
- K-factors and conversion rates (K-factor target >0.5 at D30)
- Specific product parameters (deity image library minimum 20 images per deity at V1)

---

### Coined Terms and Defined Concepts

If a term was specifically defined or coined in the conversation, capture the definition. Don't assume future Claude will infer it.

Examples:
- "Spiritual Context Engine (SCE): the AI layer that understands each user's faith profile and serves the right expression of their faith at the right moment. Called the structural moat because it requires deep domain knowledge of Sanatan dharma, regional traditions, deity-specific customs, festival calendar, and scripture — synthesised by AI. Cannot be replicated by a generic platform."
- "Digital Seva: the community contribution model where contributors are honoured (Sevak badge, leaderboard, featured placement) rather than paid. Replaces tokenisation which was rejected."
- "Rate limiting strategy: token bucket per user at the API gateway, with a separate lower limit for unauthenticated requests. Burst capacity of 10x sustained rate for authenticated users to handle legitimate spikes. Redis-backed counters with 1-second resolution."

---

### Standing Instructions

If the user gave any instructions about how Claude should behave in this project, they belong in the memory.

Examples:
- "All documents should be formatted for MS Word / Google Docs copy-paste"
- "Video prompts default to 9:16 vertical format unless told otherwise"
- "Never suggest AI-generated deity imagery"
- "The admin surface is a content safety system, not a log viewer — do not propose monitoring-only designs"

---

### Current Status and Next Steps

The memory should tell future Claude exactly where to pick up.

Not: "We were working on the brainstorm."
But: "Framework stack status: Layer 1 (Moments Map) ✅, Layer 2 (JTBD all 6 apps) ✅, Layer 3 (Hooked Model + Habit Chain) ✅, Layer 4 (Value Proposition Canvas) → NEXT STEP, Layer 5 (Viral Loop) → pending, Layer 6 (Constellation Layer) → pending."

---

## What NOT to Capture

### Conversational filler
Small talk, pleasantries, clarifying questions that were answered — these don't belong in the memory.

### Superseded information
If a decision was made and then revised in the same conversation, only capture the final decision (with a note that it was revised from an earlier position if that context matters).

### Highly speculative ideas that went nowhere
If an idea was floated briefly and immediately dropped without real discussion, it doesn't need to be in the memory. If it was explored for 5+ messages before being rejected, it belongs — with its rejection reason.

---

## Memory Size Guide

| Conversation length | Recommended summary length |
|---|---|
| Under 20 messages | 500–800 words |
| 20–50 messages | 800–1,500 words |
| 50–100 messages | 1,500–2,500 words |
| 100+ messages (deep session) | 2,500–4,000 words |

There is no penalty for being thorough. The summary injects into Claude's context at the start of a new session — at 3,000 words, it uses approximately 750 tokens, which is a small fraction of Claude's context window. The cost of being too detailed is minimal. The cost of losing critical context is high.
