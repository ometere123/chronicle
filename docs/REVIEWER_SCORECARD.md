# Chronicle reviewer scorecard

| Dimension | Implementation | Evidence | Limitation |
|---|---|---|---|
| Originality | Persistent temporal partial-order graph | transitive Direct Mode test; live A/C proof | Semantic judgement depends on validators |
| GenLayer necessity | Independent web fetch and LLM observation | GenVM lint; finalized relation receipts | Public evidence is not cryptographic truth |
| Validator design | Relation, time kind, availability and support-count agreement | `validate()` and supported receipt test | Free-form explanation is audit metadata |
| State architecture | Sealed definitions and timeline/event hashes | hash-pinning tests; `proof/studionet.json` | Timelines are bounded to 16 events |
| Graph invariants | Cycle and prospective non-strict contradiction checks | overlap/SAME_WINDOW regression tests | Conflicts are surfaced, not adjudicated |
| Uncertainty | Retryable UNAVAILABLE/UNRESOLVED states | Direct Mode retry/error tests | Retry depends on later availability |
| Security | HTTPS boundary and untrusted prompt delimiters | preflight and source tests | Runtime DNS/egress assumptions remain external |
| Testing | Static, preflight, Direct Mode, lint and validation layers | 30/30 preflight; 12 static; 35 Direct Mode; lint PASS | Validator diversity is network-dependent |
| Validator disagreement | Validator re-observation rejects relation, time-kind, availability and support mismatches | Four `run_validator()` adversarial tests | Direct harness models disagreement; network validator diversity remains external |
| Retry lifecycle | Non-final uncertainty preserves attempts and permits later conclusive resolution | unavailable/unresolved retry tests | External source/model recovery is variable |
| Proof reproducibility | Canonical Keccak hashes are recomputed locally | `scripts/verify_proof.py` | Script uses the installed Keccak implementation |
| Live proof | A/B and B/C direct, A/C and C/A inferred | `proof/studionet.json` and on-chain reads | Public pages may change later |
| Composability | `IChronicle`, `is_before`, `get_before_path` | `examples/consumer.py` | Consumer must trust its configured address |

Use `is_before()` or the `graph_*` fields for settlement logic. Direct fields
are for audit and conflict visibility.
