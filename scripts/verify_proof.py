"""Offline verification of the committed StudioNet proof artifact."""

import json
from pathlib import Path

from Crypto.Hash import keccak


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "proof" / "studionet.json"


def canonical_keccak(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    digest = keccak.new(digest_bits=256)
    digest.update(encoded)
    return digest.hexdigest()


def main():
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    events = proof["events"]
    ordered = [events[key] for key in ("A", "B", "C")]
    ok = True
    hashes = []
    for key, event in zip(("A", "B", "C"), ordered):
        actual = canonical_keccak({"label": event["label"], "definition": event["definition"], "sources": event["sources"]})
        expected = event["definition_hash"]
        passed = actual == expected
        ok &= passed
        hashes.append(actual)
        print(f"event {key} hash: {'PASS' if passed else 'FAIL'}")

    timeline = proof["timeline"]
    actual_timeline = canonical_keccak({"name": timeline["name"], "purpose": timeline["purpose"], "events": hashes})
    timeline_ok = actual_timeline == timeline["timeline_hash"] == proof["timeline_hash"]
    ok &= timeline_ok
    print(f"timeline hash: {'PASS' if timeline_ok else 'FAIL'}")

    structure_ok = (
        proof["relations"]["A_B"]["relation"] == "BEFORE"
        and proof["relations"]["A_B"]["source"] == "DIRECT"
        and proof["relations"]["B_C"]["relation"] == "BEFORE"
        and proof["relations"]["B_C"]["source"] == "DIRECT"
        and proof["relations"]["A_C"] == {"relation": "BEFORE", "source": "INFERRED", "graph_finalized": True, "direct_finalized": False}
        and proof["relations"]["C_A"] == {"relation": "AFTER", "source": "INFERRED", "graph_finalized": True, "direct_finalized": False}
        and proof["before_path_A_C"] == [1, 2, 3]
        and proof["is_before_A_C"] is True
        and proof["resolved_A_C"] is False
        and proof["latest_attempt_id_A_C"] == 0
    )
    ok &= structure_ok
    print(f"transitive proof structure: {'PASS' if structure_ok else 'FAIL'}")
    print(f"proof verification: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
