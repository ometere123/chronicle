# Chronicle — Intelligent Contract Submission

## One-line purpose

Chronicle is a reusable GenLayer primitive that resolves **temporal relationships between public events** and accumulates consensus results into a deterministic, cycle-safe partial-order graph.

## Why GenLayer is necessary

Chronology is semantic rather than merely arithmetic. Public sources expose publication timestamps, retrospective reporting, incomplete intervals and sometimes contradictory narratives. A deterministic contract cannot reliably decide whether a timestamp describes the event itself or merely when somebody wrote about it.

Chronicle uses GenLayer consensus only for that semantic observation. Every validator independently fetches the frozen evidence sources and independently derives a bounded temporal relation. Deterministic contract code then decides whether the result can safely mutate shared chronology.

## Consensus fields

Validators compare state-changing fields, not just output format:

- `relation`;
- `left_time_kind`;
- `right_time_kind`;
- normalized `left_support_count` and `right_support_count`;
- non-zero supporting evidence on both sides for conclusive relations.

`reason_code`, `evidence`, `left_anchor` and `right_anchor` are bounded leader
explanatory metadata. They are persisted for auditability but are not compared
as arbitrary prose by validators.

## State machine

```text
Timeline: OPEN -> SEALED

Pair attempts:
UNAVAILABLE / UNRESOLVED / EVIDENCE_CONFLICT -> retryable
BEFORE / AFTER / OVERLAPS / SAME_WINDOW      -> finalized
cycle/invariant violation                    -> GRAPH_CONFLICT + finalized
```

## Persistent primitive value

Chronicle is deliberately not one-request/one-receipt infrastructure. Once the graph contains:

```text
A < B
B < C
```

future consumers can derive `A < C` with no additional AI or web call. Shared state becomes more useful as accepted relations accumulate.

## Deterministic safety invariants

- event definitions and source sets are immutable;
- a timeline must be sealed before resolution;
- the sealed `timeline_hash` pins the complete event-definition universe;
- only strict BEFORE edges enter the graph;
- a new edge is rejected if it would create a cycle;
- OVERLAPS/SAME_WINDOW cannot overwrite an already implied strict ordering;
- candidate strict edges are checked across `predecessors(X) × successors(Y)`
  against finalized OVERLAPS/SAME_WINDOW pairs before graph mutation;
- final pair results cannot be overwritten;
- every receipt pins its timeline and both event hashes.

## Reusability

The contract exposes `IChronicle` and reusable views:

```python
is_before(timeline_id, a, b)
get_relation(timeline_id, a, b)
get_before_path(timeline_id, a, b)
```

Potential consumers include insurance, governance, SLA enforcement, supply chains, prediction settlement, contract termination, agent workflows and compliance systems.

## Security

- source pages are untrusted prompt data;
- validators re-fetch and re-derive the decision;
- source URLs use a conservative public-HTTPS/SSRF gate;
- source, event and graph sizes are bounded;
- private evidence is intentionally unsupported;
- there are no payable methods or value-transfer paths.

## Testing

The repository includes GenLayer Direct Mode coverage plus dependency-free preflight/static checks. The current behavioral suite has 42 passing tests, including retry lifecycles, prompt-injection-like source text, four-node cycles, overlap-vs-order conflicts, unavailable evidence, immutable definitions and receipt hash pinning.

## Category fit

Chronicle has no frontend and no application product flow. It is intentionally a standalone Intelligent Contract primitive for other builders to compose.

## Deployment status

Final verified StudioNet deployment:

- contract: `0xa225F86B51ECE63b2d41A8856C33b6366cA1f344`;
- deployment transaction: `0x378c703e73afa88f991ad3ecd209d5da039f6a92cc96e9182538abb3fdc84cf4`;
- deployer: `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2`;
- deployed source commit: `f294ebf2934140d4e7718e8712097db62818ddf0`;
- status: FINALIZED / SUCCESS.

The machine-readable lifecycle is in `proof/studionet.json`.

## Reviewer test plan

```bash
python scripts/preflight.py
pip install -r requirements-dev.txt
pytest -q tests/test_static.py
gltest tests/test_chronicle.py -v -s
```

For the live value proof, create three events, seal the timeline, resolve A/B
and B/C, then call `get_relation(A, C)`. The result should report
`BEFORE` with `source = INFERRED`; no third resolution is required. The cycle
and graph-conflict proof is kept in the Direct Mode suite so it does not require
fabricating contradictory public evidence.
