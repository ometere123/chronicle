# Chronicle Architecture

## Objective

Chronicle separates temporal adjudication into two layers with different trust models:

1. **semantic observation** — nondeterministic, source-grounded and validator-consensus controlled;
2. **chronology consistency** — deterministic graph mutation with explicit invariants.

## Definition phase

A timeline owner creates an OPEN timeline and adds 2–16 events. Each event contains a label, a precise semantic definition, 1–4 public HTTPS sources and a deterministic definition hash.

No event-update API exists. The owner can append only while the timeline is OPEN. `seal_timeline` hashes the ordered event-definition hash list with the timeline name and purpose, producing a permanent `timeline_hash` namespace for later receipts.

## Observation phase

Event pairs are canonicalized by ID so argument order cannot create duplicate logical pairs. The nondeterministic observer independently fetches each source, marks unavailable responses, truncates prompt evidence to a bounded size and asks the model for one bounded temporal relation plus time-kind classifications.

The validator reruns the same observer and compares the decision fields that can change state.

## Why time-kind is part of consensus

A model can reach the correct apparent order for the wrong reason, especially by comparing article publication timestamps rather than when the defined events actually occurred. Chronicle therefore requires conclusive validator agreement on:

```text
relation
left_time_kind
right_time_kind
```

## Graph phase

Only `BEFORE`, `AFTER`, `OVERLAPS` and `SAME_WINDOW` can become pair-final.

Strict order is represented only as directed BEFORE edges.

Before adding `A -> B`, Chronicle checks whether `B -> ... -> A` already exists. If it does, the semantic observation remains in the receipt but the effective result becomes `GRAPH_CONFLICT` and no edge is written.

`AFTER` is normalized to the reverse BEFORE edge. `OVERLAPS` and `SAME_WINDOW` add no strict edge and become graph conflicts if an existing path already proves strict order in either direction.

## Retry model

`UNAVAILABLE`, `UNRESOLVED` and `EVIDENCE_CONFLICT` are intentionally not pair-final. Event definitions and source sets remain frozen, but a public source may later become reachable or publish clarifying information. Every attempt is retained as an immutable receipt.

## Query model

`get_relation` checks:

1. finalized direct pair result;
2. transitive strict-order path;
3. latest retryable attempt;
4. unresolved.

`is_before` and `get_before_path` query only the deterministic graph, allowing downstream contracts to consume established chronology without invoking consensus again.

## Bounded complexity

`MAX_EVENTS = 16` bounds graph traversal. At this scale straightforward traversal keeps writes small, makes invariants easy to audit and avoids maintaining a larger transitive-closure matrix.

## Receipt integrity

Every relation receipt pins:

```text
timeline_hash
left_event_hash
right_event_hash
```

A consumer can therefore verify that a result belongs to the exact sealed event universe it expected.
