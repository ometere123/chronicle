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
```

or deploy explicitly:

```bash
genlayer deploy \
  --contract contracts/chronicle.py \
  --rpc https://studio.genlayer.com/api
```

Chronicle has no constructor arguments.

## 4. Record real deployment proof

After a finalized deployment, record:

```text
contract address:
deploy transaction:
network:
commit SHA:
```

Do not invent values. Copy them from finalized CLI/Explorer output.

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
