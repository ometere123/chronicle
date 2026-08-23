# Chronicle

**Consensus-backed event chronology for GenLayer.**

Chronicle is a standalone reusable Intelligent Contract that resolves temporal relationships between publicly evidenced events and accumulates accepted results into a deterministic, cycle-safe partial-order graph.

There is **no frontend and no backend**. Chronicle is intentionally a contract primitive for the Intelligent Contracts category.

## Problem

Many settlement rules depend not only on whether facts are true, but on **ordering**:

- Was cancellation effective before fulfillment?
- Was a governance veto issued before execution became final?
- Did custody transfer before cargo damage occurred?
- Did an incident happen before insurance coverage began?
- Was a security disclosure made before an upgrade?

A naive oracle can confuse article publication time with event time, force false timestamp precision, or produce pairwise answers that form an impossible cycle. Chronicle is designed around those failure modes.

## Primitive

A timeline moves through two deterministic states:

```text
OPEN -> SEALED
```

While open, its owner registers 2–16 immutable event definitions and 1–4 public HTTPS evidence sources for each event. Sealing freezes the event universe and computes a `timeline_hash` over all event-definition hashes.

After sealing, **any caller** can invoke:

```text
resolve_relation(timeline_id, event_a, event_b)
```

Consensus can return:

```text
BEFORE
AFTER
OVERLAPS
SAME_WINDOW
EVIDENCE_CONFLICT
UNRESOLVED
UNAVAILABLE
```

A deterministic graph-consistency layer may convert an otherwise conclusive answer into:

```text
GRAPH_CONFLICT
```

when accepting it would contradict chronology already established.

## Why the state compounds

Suppose consensus establishes:

```text
A BEFORE B
B BEFORE C
```

Chronicle can now answer:

```text
A BEFORE C
```

**without another web fetch or LLM call.**

If a later direct observation for `(A, C)` claims `A AFTER C`, Chronicle preserves the semantic observation in an immutable receipt but records the effective result as `GRAPH_CONFLICT` and refuses to add the cycle.

```text
external evidence
      ↓
GenLayer semantic consensus
      ↓
observed relation
      ↓
deterministic graph consistency
      ↓
effective relation / reusable partial order
```

## Consensus design

All web requests and LLM calls happen inside `gl.vm.run_nondet_unsafe`.

The leader independently:

1. fetches every frozen source for the left event;
2. fetches every frozen source for the right event;
3. records failed/HTTP-error sources as unavailable;
4. treats all fetched content as untrusted prompt data;
5. derives a bounded temporal relation and time-kind classification;
6. canonicalizes the result.

Each validator repeats the **same substantive observation**. It does not merely validate JSON shape.

For a semantically final result, leader and validator must agree on:

- temporal relation;
- left time-kind;
- right time-kind;
- non-zero supporting evidence on both sides.

Free-form reasoning prose and human-readable anchors do not need exact equality.

## Time-kind model

Chronicle stores how the relevant timestamp was interpreted:

| Kind | Meaning |
|---|---|
| `EVENT_TIME` | directly describes when the defined event occurred |
| `PUBLICATION_TIME` | only establishes when a source was published |
| `REPORTED_TIME` | retrospectively reports when the event happened |
| `OBSERVED_TIME` | only validator observation/fetch time is known |
| `UNKNOWN` | the temporal anchor cannot be classified safely |

The validator prompt explicitly states:

> Publication time is NOT automatically event time.

An article published on August 23 can describe an event that occurred on August 20.

## State design

### Timeline

```text
owner
name
purpose
status
created_at
sealed_at
timeline_hash
event_ids[]
```

### EventNode

```text
timeline_id
label
definition
created_at
definition_hash
source_urls[]
```

### RelationReceipt

Every attempt pins:

```text
timeline_hash
left_event_hash
right_event_hash
observed_relation
effective_relation
time kinds
source availability/support counts
graph_applied
finalized
reason code
evidence summary
anchors
observation time
```

`UNAVAILABLE`, `UNRESOLVED`, and `EVIDENCE_CONFLICT` remain retryable because frozen public sources may later become reachable or clearer. Conclusive pair results become final.

## Graph invariants

Chronicle stores only strict `BEFORE` edges.

Before adding `A -> B`, deterministic logic checks whether a path already exists from `B -> A`. If yes:

```text
observed: BEFORE
effective: GRAPH_CONFLICT
graph_applied: false
```

`OVERLAPS` and `SAME_WINDOW` are also rejected as graph conflicts if a strict path is already established in either direction.

## Public API

### Write

```python
create_timeline(name: str, purpose: str) -> u256
add_event(timeline_id: u256, label: str, definition: str, sources_json: str) -> u256
seal_timeline(timeline_id: u256) -> str
resolve_relation(timeline_id: u256, event_a: u256, event_b: u256) -> u256
```

### Views

```python
get_timeline(timeline_id)
get_event(event_id)
get_relation_receipt(relation_id)
get_relation(timeline_id, event_a, event_b)
is_before(timeline_id, event_a, event_b)
get_before_path(timeline_id, event_a, event_b)
is_pair_finalized(timeline_id, event_a, event_b)
latest_attempt_id(timeline_id, event_a, event_b)
```

## Cross-contract composition

Chronicle exposes `IChronicle` so downstream contracts can consume established chronology without repeating semantic work:

```python
if chronicle.view().is_before(timeline_id, cancellation_event, fulfillment_event):
    # deterministic consumer policy
    ...
```

Potential consumers include insurance, governance, SLA enforcement, supply-chain logic, prediction settlement, agent workflows, incident analysis and compliance systems.

## Security boundaries

- fetched pages are explicitly delimited as **untrusted source data**;
- validators re-fetch and independently re-derive state-changing fields;
- evidence URLs use a conservative public-HTTPS/SSRF gate;
- event/source/graph sizes are bounded;
- source definitions are immutable and timeline sealing prevents evidence-universe mutation;
- cycle-producing strict relations are rejected deterministically;
- private/authenticated evidence is intentionally unsupported;
- there are no payable methods or value-transfer paths.

## Testing

```bash
python scripts/preflight.py
pip install -r requirements-dev.txt
pytest -q tests/test_static.py
gltest tests/test_chronicle.py -v -s
```

The Direct Mode suite covers registration, ownership, source safety, sealing, permissionless resolution, relation inversion, transitive inference, cycle rejection, graph conflicts, unavailable/unresolved evidence and receipt definition-hash pinning.

See [docs/WHY_CHRONICLE_IS_A_PRIMITIVE.md](docs/WHY_CHRONICLE_IS_A_PRIMITIVE.md) for the technical contribution and reviewer proof strategy.

## Deployment

```bash
npm install -g genlayer
genlayer network studionet
genlayer deploy --contract contracts/chronicle.py
```

Or explicitly:

```bash
genlayer deploy --contract contracts/chronicle.py --rpc https://studio.genlayer.com/api
```

Chronicle has no constructor arguments. Record the final address, deployment transaction, network and commit SHA in `docs/DEPLOYMENT.md` after a real finalized deployment. Never invent deployment proof.

## Repository layout

```text
contracts/chronicle.py       core Intelligent Contract
examples/consumer.py         composition example
tests/test_chronicle.py      GenLayer Direct Mode tests
tests/test_static.py         dependency-free architecture checks
scripts/preflight.py         reviewer/pre-deployment preflight
docs/ARCHITECTURE.md         design and invariants
docs/THREAT_MODEL.md         security analysis
docs/DEPLOYMENT.md           live proof checklist
SUBMISSION.md                 portal/reviewer summary
```

## What Chronicle is not

Chronicle is not a generic factual oracle, dispute court, escrow, publication timestamp scraper, or free-form LLM wrapper. Its reusable job is narrower and deeper:

> turn independently observed public evidence into a consensus-backed, cycle-safe temporal partial order that other contracts can query.

## License

MIT.
