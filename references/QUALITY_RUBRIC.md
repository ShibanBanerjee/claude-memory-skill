# Memory Quality Rubric

## Scoring a Memory Entry

### Is the summary self-contained? (Critical)
A future Claude reading ONLY this summary should know everything
a Claude who participated in the conversation would know.
If it would need to ask clarifying questions, the summary is incomplete.

### Does it capture WHY? (Critical)
Every decision must have its reason.
"Chose Option B" is incomplete.
"Chose Option B because X; Option A was rejected because Y" is complete.

### Does it capture rejections? (Critical)
Every significant option that was considered and rejected must appear
with its rejection reason. This prevents future Claude from re-proposing
ideas that were already ruled out.

### Is it specific enough? (Important)
- Named products, not "the app"
- Exact numbers, not "a lot"
- Named people, not "the founder"
- Specific frameworks, not "a framework"

### Are open questions actionable? (Important)
A future Claude should be able to immediately act on each open question
without further clarification. If it would need to ask "which project?"
or "what do you mean?" — the question is too vague.

### Are instructions captured? (Important)
Any time the user said "always do X" or "never do Y" or expressed a
preference about how Claude should behave — it must be in instructions[].

## Quick Checklist
- [ ] Summary is 1,500+ words
- [ ] Every decision has its reason
- [ ] Every rejection has its reason
- [ ] Open questions are specific and actionable
- [ ] User instructions are captured
- [ ] All named entities are in entities{}
- [ ] Tags would be found by a future search
- [ ] Summary is self-contained (no unexplained references)
