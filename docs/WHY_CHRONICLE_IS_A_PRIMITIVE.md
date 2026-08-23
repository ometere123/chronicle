# Why Chronicle Is a Primitive

Chronicle is not a thin LLM wrapper or a timestamp database. It is a reusable
consensus-backed state machine for building temporal knowledge that remains
useful after the original semantic observation has finished.

## What the contract contributes

1. **Frozen event semantics.** Event definitions and their public evidence
   sources are registered before sealing. Definition hashes and the sealed
   timeline hash pin exactly what validators were asked to resolve.
2. **Validator-reobserved evidence.** The leader fetches and interprets the
   sources inside nondeterministic execution. Validators fetch the same frozen
   sources and independently reproduce the state-changing decision fields.
3. **Event time is not publication time.** The bounded result includes
   `EVENT_TIME`, `PUBLICATION_TIME`, `REPORTED_TIME`, `OBSERVED_TIME`, or
   `UNKNOWN`. Publication order is never treated as event order automatically.
4. **Bounded consensus output.** Only a small enum, time kinds, support counts,
   and bounded evidence are persisted. Free-form model prose is not used as
   graph truth.
5. **Immutable relation receipts.** Every attempt records the canonical pair,
   observed/effective relation, evidence availability, anchors, timestamps,
   and all relevant hashes. Retryable attempts are retained rather than
   rewritten.
6. **Deterministic DAG mutation.** Consensus proposes a fact; deterministic
   contract code decides whether that fact can enter the chronology graph.
7. **Transitive inference.** If `A BEFORE B` and `B BEFORE C` are accepted,
   `A BEFORE C` is available from a bounded graph traversal with no third
   web fetch or LLM call.
8. **Cycle resistance.** An attempted edge that would create a directed cycle
   becomes a `GRAPH_CONFLICT` receipt and does not mutate established state.
9. **Uncertainty preservation.** `UNAVAILABLE`, `UNRESOLVED`, and
   `EVIDENCE_CONFLICT` remain retryable. Chronicle does not turn an outage or
   ambiguous evidence into false certainty, and it does not force a total order
   when the partial order does not justify one.
10. **Cross-contract consumption.** Other Intelligent Contracts can call
    `is_before` and `get_relation` through `IChronicle`; consumers reuse facts
    already established on-chain instead of repeating semantic inference.

## Why state compounds

Each accepted strict relation adds a durable edge to a shared timeline. The
value of the timeline therefore grows with independent pairwise resolutions:

```text
evidence -> validator consensus -> direct edge -> inferred paths -> consumers
```

The graph is deliberately a partial order. If two events have no provable
relationship, that uncertainty is more honest and safer for downstream policy
than inventing a numerical sort position.

## Consensus boundary

GenLayer is necessary for the semantic boundary: heterogeneous public sources
must be fetched and interpreted independently by validators. Deterministic
contract code is better suited to the rest of the job: hash pinning, bounded
storage, pair canonicalization, finality, graph mutation, cycle checks, and
machine-readable queries.

## Reviewer proof

The minimal demonstration is:

```text
resolve(A, B) -> BEFORE (DIRECT)
resolve(B, C) -> BEFORE (DIRECT)
get_relation(A, C) -> BEFORE (INFERRED)
```

The last result is derived from persistent state and does not invoke the
nondeterministic observer again. The adversarial Direct Mode test then attempts
the reverse of an established path and verifies an immutable graph-conflict
receipt with `graph_applied = false`.
