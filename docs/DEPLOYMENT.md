# Deployment and Reviewer Proof

## 1. Install current CLI

```bash
npm install -g genlayer
genlayer --version
```

## 2. Run checks

```bash
python scripts/preflight.py
pip install -r requirements-dev.txt
pytest -q tests/test_static.py
gltest tests/test_chronicle.py -v -s
```

## 3. Select StudioNet

```bash
genlayer network studionet
genlayer account show
genlayer deploy --contract contracts/chronicle.py
```

Chronicle has no constructor arguments.

## 4. Verified deployment

The final source commit is `f294ebf2934140d4e7718e8712097db62818ddf0` and the
contract source SHA-256 is
`FADC2F7AA214973C1F9D3C1C26F866B092D9938CCF55D95C1A4CFDFBDB2B67D7`.

```text
network: studionet
contract: 0xa225F86B51ECE63b2d41A8856C33b6366cA1f344
deployment tx: 0x378c703e73afa88f991ad3ecd209d5da039f6a92cc96e9182538abb3fdc84cf4
deployer: 0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2
status: FINALIZED / SUCCESS
timeline: 1
timeline hash: b515c110bb1ec6754c9ec218293d4c12782d99dcbd2d15d978cd6247858c60cf
```

The complete transaction and relation record is `proof/studionet.json`.

Verification recorded in `proof/verification.json`:

- preflight: 30/30;
- static tests: 12 passed;
- Direct Mode: 35 collected and 35 passed;
- GenVM lint/validation: PASS, 12 methods;
- local proof hash verification: PASS.

Run `python scripts/verify_proof.py` to recompute the Keccak-256 event and
timeline hashes without a live network connection.

## 5. Reviewer lifecycle

Use two or three public sources with an unambiguous chronology:

1. `create_timeline`
2. `add_event` for A
3. `add_event` for B
4. optionally `add_event` for C
5. `seal_timeline`
6. record `timeline_hash`
7. permissionless `resolve_relation(A, B)`
8. permissionless `resolve_relation(B, C)`
9. `get_relation(A, C)` and show `source = INFERRED`
10. `get_before_path(A, C)`

The important proof is that step 9 requires no additional semantic resolution.

The recorded proof has A/B relation ID 1 and B/C relation ID 2, both
`BEFORE` / `DIRECT`; A/C is `BEFORE` / `INFERRED`, C/A is `AFTER` /
`INFERRED`, and the path is `[1, 2, 3]`.

## 6. Adversarial proof

Direct Mode should establish `A < B < C` and then attempt a contradictory direct `(A, C)` result. The expected outcome is an immutable receipt whose observed relation is retained but whose effective relation is `GRAPH_CONFLICT`, with no cycle written.

Do not manufacture contradictory public facts merely for a StudioNet demo. Keep adversarial contradiction fixtures in Direct Mode unless legitimate conflicting evidence exists.

## 7. Explorer verification

Verify that:

- deployed source matches the repository commit;
- `get_timeline` exposes the sealed hash;
- receipts pin that same hash and both event hashes;
- reverse orientation resolves correctly;
- inferred paths are queryable;
- the submission remains a standalone contract with no frontend requirement.
