# Encore

A ListenBrainz music agent that remembers. Encore answers questions about your listening, looks up
artists and songs on MusicBrainz, recommends music, and builds and edits ListenBrainz playlists. It
asks before it changes anything in your account. It keeps four kinds of memory: working, episodic,
semantic and procedural.

CSCI 391 (Agentic AI) midterm, University of Montana, Autumn 2026. The assignment is in `../Midterm.html`.

## Contents

- [Setup](#setup)
- [Running Encore](#running-encore)
- [How it works](#how-it-works)
- [Memory design](#memory-design)
- [Retention policy](#retention-policy)
- [Privacy and deletion](#privacy-and-deletion)
- [Evaluation](#evaluation)
- [Tests](#tests)
- [Known limitations](#known-limitations)
- [Project layout](#project-layout)

## Setup

```
python -m pip install -r requirements.txt
cp .env.example .env            # Windows PowerShell: copy .env.example .env
```

Fill in `.env`:

| Variable | What it is |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter key (online mode) |
| `OPENROUTER_MODEL_CHEAP` / `_EXPENSIVE` | the model strings for the two tiers |
| `LOCAL_LLM_URL`, `LOCAL_LLM_MODEL_*` | a local llama.cpp server (offline mode) |
| `LISTENBRAINZ_TOKEN` | from listenbrainz.org → Settings. **Never commit, log, or store it.** |
| `LISTENBRAINZ_USER` | your ListenBrainz username |
| `ENCORE_USER_ID` | the key every memory is stored under, and deleted by (usually your username) |
| `CONTACT_EMAIL` | sent in the User-Agent, as MusicBrainz requires |

The token is sent only in request headers. Traces redact it, and it never enters a prompt or a
memory store. `.env`, `memory/`, `.cache/` and `knowledge/raw/` are in `.gitignore`.

Build the semantic-memory index once (and again after editing `knowledge/glossary.md`):

```
python semantic.py --build
```

## Running Encore

```
python encore.py online                      # interactive session using OpenRouter models
python encore.py offline                     # the same session using a local model server
python encore.py online --inject inject/flaky.json   # fault injection (see below)
python encore.py online --forget             # delete every memory for ENCORE_USER_ID
python encore.py online --reindex-episodic   # re-embed episodic memory after changing the embedding model
```

Type a request at `you>`. Type `quit` (or press Ctrl-D) to end the session. Episodic memory is
written when the session ends.

Example requests:

- "Who are the members of Khruangbin?"
- "What have I been listening to lately?"
- "Find me some ambient music I might like."
- "Make me a short playlist of 5 ambient songs called Rainy Day." (asks for approval before creating it)
- "How do I connect Spotify to ListenBrainz?" (answered from semantic memory)

### Fault injection

`--inject <file.json>` makes failures reproducible:

| File | Settings | Effect |
|---|---|---|
| `inject/flaky.json` | `transient_rate: 0.3, seed: 391` | 30% of ListenBrainz/MusicBrainz calls return 429/503 before reaching the network |
| `inject/outage.json` | `transient_rate: 1.0` | every API call fails |
| `inject/tight.json` | `max_steps: 2` | the step budget runs out (`budget_exceeded`) |

## How it works

`presentation/architecture.png` has the diagram. One request runs as follows:

1. **Route.** The cheap model classifies the request into tool domains (listening, catalog,
   discovery, library, memory or none), using a forced `classify_intent` call validated against
   a JSON Schema enum. If routing fails, every domain is offered. Some domains bring a companion:
   discovery and library always add catalog, because songs must be verified before they are used
   ([router.py](router.py)).
2. **Bounded ReAct loop** (at most 12 steps). The cheap model picks tools from the routed set. The
   prompt's Rules section is reinjected on every call so it can't drift. Calls to tools outside the
   routed set are refused.
3. **Tools** (18, plus `final_answer`) return a structured `{success, data, error_category, message}`.
   Empty results are errors with a message the model can act on, never a silent `[]`. Transient
   errors (429/503) are retried with backoff. `add_playlist_items` and `export_playlist` are never
   retried automatically, because a retry could apply them twice.
4. **Approval gate.** Every write tool asks `y/n` first and shows what will change. Export and delete
   always ask. `set_feedback` skips the prompt only when the user's own message named that action
   ("love this song"). Encore can delete only playlists whose titles start with `[Encore]`. After a
   declined approval, Encore doesn't retry the write.
5. **Finish.** The loop ends only through `final_answer` (the expensive model, falling back to the
   cheap one) or a termination status: `answered`, `answered_low_confidence`, `stuck`,
   `budget_exceeded` or `policy_halt`.

Every session writes one JSONL trace to `traces/`. It records each route, LLM call (model, tier,
tokens, cost, latency), tool call (arguments, attempt, error category), approval, memory read and
write, and the final status. The first line pins the prompt version and model strings.

## Memory design

| Type | Store | Holds | Written | Read |
|---|---|---|---|---|
| **Working: history** | in-process list | this session's messages and tool observations | every step | every model call |
| **Working: hot state** | SQLite, `memory/hot_state.db` | verified MBIDs, session preferences, active playlist, last recording | by tools | rebuilt into every model call |
| **Episodic** | Chroma, `memory/chroma/` | one structured summary per past session | session end | first message, and the `search_past_sessions` tool |
| **Semantic** | Chroma, `memory/semantic/` | LB/MB documentation and a 30-term music glossary | `semantic.py --build` | the `search_music_knowledge` tool |
| **Procedural** | `prompts/system_v1.md` | role, rules, memory and tool guidance | by hand, with an entry in `prompts/CHANGELOG.md` | session start; Rules on every call |

Your ListenBrainz listens, feedback and playlists are **not** Encore's memory. They are data about
the world, read with tools, and `--forget` never touches them.

### Working memory

Rules are kept outside the history and reinjected on every call. Hot state is never summarized
away: it holds the facts the agent must not lose, such as which MBIDs were verified in this session.
If one request crashes, its half-written messages are rolled back, so the next request starts from
a valid history.

### Episodic memory ([episodic.py](episodic.py))

**Write path (at session end):** the cheap model writes a structured summary (decisions,
preferences, open threads, key facts, errors, topics). A quality check compares it with the
conversation. Unsupported claims mark the summary `flagged` rather than dropping it. Then
deduplication runs, and the summary is stored with `user_id`, a timestamp, quality, and the
embedding model and version.

**Deduplication threshold: 0.93 cosine similarity.** A new summary that similar to an existing
one from the same user is merged into it, not added. 0.93 is high enough that two sessions about
the same playlist on different days stay separate (they differ in what was decided). It's low
enough that a near-identical repeat session merges instead of piling up.

**Read path (on the first message):** search filtered to this user and the last 90 days, take 10
candidates, rerank by `0.7 × similarity + 0.3 × recency` (recency halves every 30 days), weight
flagged summaries ×0.5, and inject the top 3. They arrive with a staleness instruction ("may be
outdated; today wins"), and flagged ones are marked *verify before using*.

**Embedding model change:** each summary and the collection record the embedding model. If
`ENCORE_EMBEDDING_MODEL` changes, startup detects the mismatch and refuses to run rather than mix
vectors. To re-index:

1. Set the new model in `.env` (`ENCORE_EMBEDDING_MODEL=...`).
2. Run `python encore.py online --reindex-episodic`. This re-embeds every stored summary from its
   saved text.
3. Start Encore normally.

The semantic index is rebuilt from the corpus with `python semantic.py --build`.

### Semantic memory ([semantic.py](semantic.py))

The corpus has 24 documents (~43k words): 15 ListenBrainz documentation pages, 8 MusicBrainz API
and data-model pages, and `knowledge/glossary.md`. The HTML pages are converted to Markdown by
`knowledge/convert_docs.py`.

`knowledge/experiment.py` compared two chunking strategies and one improvement, on 31 questions
with known answers. Every chunk is ≤ 256 tokens, the embedding model's limit, measured with the
model's own tokenizer.

| Configuration | Chunks | Max / mean tokens | Recall@1 | Top-3 recall |
|---|---|---|---|---|
| Fixed 256-token windows, 32 overlap (vector) | 455 | 256 / 248 | 15/31 | 21/31 (68%) |
| One chunk per heading section (vector) | 661 | 256 / 170 | 12/31 | 24/31 (77%) |
| **Sections + hybrid (BM25 + vector, reciprocal rank fusion)** | 661 | 256 / 170 | 13/31 | **25/31 (81%)** |

Encore uses sections + hybrid search. The tool returns 3 passages, so top-3 recall is the
number that matters. Every miss is listed in `knowledge/results.md`.

## Retention policy

| Store | Policy | Status |
|---|---|---|
| History | lives for one session only | implemented |
| Hot state, session keys (`verified_recordings`, `session_preferences`, `tool_call_count`) | cleared at the start of each session | implemented |
| Hot state, carryover keys (`active_playlist`, `last_recording`) | expire 24 hours after they're written | implemented |
| Episodic summaries | TTL of 90 days: older summaries are not retrieved | implemented (enforced at retrieval) |
| Episodic summaries | cap of 50 most recent summaries per user | **not implemented** |
| Episodic summaries | summarize then archive: past the TTL, standing preferences are promoted to a long-term preference store, then the originals are removed | **not implemented** |
| Semantic index | no expiry; rebuilt from the corpus on demand | implemented |
| Traces | kept for evaluation; they contain no token or headers | implemented |

A `--now` option to simulate time passing is **not implemented**. The retention functions accept a
`now` argument, which the unit tests use.

## Privacy and deletion

`python encore.py online --forget` deletes every item stored under `ENCORE_USER_ID` from hot
state and episodic memory, and prints how many items were deleted from each store. It never calls
ListenBrainz. The semantic index holds no personal data, so it's left alone.
`tests/unit/test_forget.py` checks that nothing remains afterward.

## Evaluation

```
python eval/run_eval.py online               # the 30 requests in eval/requests.json (run 1)
python eval/run_eval.py online --variance    # 5 of them, runs 2 and 3
python eval/run_eval.py online --memory      # the two-session scenarios in eval/memory_scenarios.json
python eval/run_eval.py online --only H01,B08   # selected requests
python eval/score.py                         # traces → eval/results.csv and eval/summary.md
python eval/tables.py [--markdown]           # display the tables (pandas; --markdown needs tabulate)
python knowledge/experiment.py               # the retrieval experiment → knowledge/results.md
```

Each run is a real Encore session with scripted input and scripted approvals. The correct outcome
of every request was written before running. Evaluation uses its own memory in `memory/eval/`, so
it never reads or changes your own memories. The scorer reads only traces. Run full evaluations off
campus (the APIs rate-limit by IP).

Results (run 1, cost from OpenRouter's reported usage):

| Category | Correct | Mean latency | Mean cost | Peak tokens in |
|---|---|---|---|---|
| Happy path | 8/10 | 13.3 s | $0.00095 | 3,772 |
| Boundary | 8/10 | 18.0 s | $0.00078 | 69,205 |
| Failure | 10/10 | 8.3 s | $0.00057 | 3,901 |
| **All 30 requests** | **26/30 (87%)** | 13.2 s | $0.00077 | 69,205 |
| Memory scenarios | 1/2 (M01–M02 only) | 14.9 s | $0.00135 | 6,171 |

**Variance:** H01, H02, H03, H04 and H06 each ran 3 times, with the same status and the same
number of tool calls every time. Only latency varied (H06: 17.0–27.7 s).

The runs that failed are explained in `eval/summary.md`. Their traces are starred in `traces/`
(for example `traces/* B08 …jsonl`).

## Tests

```
python -m pytest tests/unit     # offline (fake network and clock), about 2 seconds, 192 tests
python -m pytest tests/live     # real ListenBrainz and MusicBrainz APIs, read-only (not during class)
ENCORE_WRITE_TESTS=1 python -m pytest tests/live/test_live_writes.py -v   # opt-in write round trips
```

The write round trips create a private `[Encore test] …` playlist on your account, edit it and
delete it. They also love a recording and then restore your previous feedback. If one prints
`CLEANUP FAILED`, fix that item by hand on listenbrainz.org.

## Known limitations

- **Bad `final_answer` calls.** The expensive model (Llama 3.1 70B) sometimes fills the forced
  `final_answer` call with another tool's arguments, or with almost nothing. Encore rejects it and
  retries with the cheap model, but if both fail, the status is `stuck` and the answer the model
  had already written is lost. This caused H07, B04 and M01, and it's the first thing to fix:
  fall back to the last step's text.
- **No repeat detection.** In B08 ("my last 500 listens"), the model called `get_recent_listens(100)`
  with the same arguments 12 times, until the step budget ran out.
- **No context compression.** History grows without a bound inside a session. B08 reached 69,205
  input tokens on one call. The design (summarize old observations past a token budget, log a
  `compress` trace event) is not built.
- **Routing errors limit the tools.** The cheap router sent "Love the song Tech Noir" to memory
  instead of library, so `set_feedback` was never offered (H10).
- **Preferences don't persist directly.** `note_preference` keeps a preference for the current
  session only. Later sessions see it only through the episodic summary. If that summary is
  flagged, the preference may not be used (M01).
- **Retention is partial.** The 50-summary cap, archive with preference promotion, and `--now`
  are not implemented (see [Retention policy](#retention-policy)).
- **Cost may be undercounted.** OpenRouter reported $0 for some paid calls (one 69k-token call in
  B08), so the totals are a lower bound.
- **Small evaluation sets.** 31 retrieval questions (one question ≈ 3 points of recall) and only
  2 of 5 memory scenarios completed. Variance was tested only on easy requests.
- **Strict recall scoring.** A retrieval hit needs the exact answer phrase in a chunk, so a passage
  that answers in different words counts as a miss.

## Project layout

```
encore.py              the agent: tools, approval gate, ReAct loop, session start/end, CLI
router.py              tool-domain routing (cheap model) and companion domains
llm.py                 OpenRouter / local model calls, tiers, retries, cost
schemas.py             JSON Schemas for every tool and final_answer
tracer.py              JSONL traces with token redaction
hot_state.py           working-memory hot state (SQLite)
episodic.py            episodic memory: summarize, quality check, dedup, retrieve, forget, reindex
semantic.py            semantic memory: chunking, Chroma index, hybrid search
prompts/               procedural memory: system_v1.md and CHANGELOG.md
knowledge/             corpus/, glossary.md, questions.json, experiment.py, results.md
eval/                  requests.json, memory_scenarios.json, run_eval.py, score.py, tables.py, results
inject/                fault-injection settings
traces/                one JSONL trace per session
presentation/          architecture diagram
tests/unit, tests/live offline and live tests
memory/                all memory stores (gitignored)
```
