# Retrieval and Context Restoration Spec

## After Retrieving a Memory

After a successful /context retrieval, Claude must:

1. Show the user a clear confirmation of what was loaded
2. Immediately USE the context — treat all fields as fully known
3. Not re-ask for information already in the memory
4. Resume from where the open_questions left off
5. Apply any instructions[] found in the memory

## Confirmation Format

```
Memory loaded: "[title]"
Saved: [date] | Project: [project] | Words: ~[N]
[N] decisions locked | [N] open questions | [N] instructions

Context restored. [One sentence summary of where things stand.]
[If open questions exist: "Next step was: [first open question]"]

Where would you like to continue?
```

## Handling Multiple Results

If search returns 2–3 memories, show a brief list and ask which to load.
If search returns 0 results, suggest broader terms and offer to list all.

## Handling Stale Memories

If a memory is more than 30 days old, note it:
"Note: this memory is from [N] days ago. Some context may have changed."
