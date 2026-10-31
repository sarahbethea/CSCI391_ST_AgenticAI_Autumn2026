# System prompt changelog

Each entry: what changed, and why (cite the trace line that showed the problem when there is one).

## v1 (2026-10-29)
- Initial version: Role, Rules (reinjected on every model call), Memory, and Tools sections.
- Rules cover the graded behaviors: approval for writes, verify-before-write, no invented songs, the
  `[Encore]` delete limit, duplicate check before create, no retry after a declined approval, honest
  failure reporting, untrusted data, and never handling the token.
- Memory covers staleness ("today wins"), "verify before using" summaries, note_preference, references
  within the conversation, and listening data vs. episodic memory.
- Tools covers memory routing, the playlist workflow, where IDs come from, what to do per error category,
  the step budget, and how to finish.
