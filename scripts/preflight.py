from pathlib import Path
import ast
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "chronicle.py"
README = ROOT / "README.md"
SUBMISSION = ROOT / "SUBMISSION.md"

checks = []


def check(name, condition):
    checks.append((name, bool(condition)))


text = CONTRACT.read_text(encoding="utf-8")
readme = README.read_text(encoding="utf-8")
submission = SUBMISSION.read_text(encoding="utf-8")

try:
    ast.parse(text)
    parses = True
except SyntaxError:
    parses = False

check("contract parses", parses)
check("py-genlayer dependency pin present", '"Depends": "py-genlayer:' in text)
check("Chronicle contract exists", "class Chronicle(gl.Contract)" in text)
check("cross-contract interface exists", "class IChronicle" in text)
check("custom validator reruns observer", "follower = observe()" in text)
check("run_nondet_unsafe used", "gl.vm.run_nondet_unsafe(observe, validate)" in text)
check("live web evidence used", "gl.nondet.web.request" in text)
check("LLM semantic resolution used", "gl.nondet.exec_prompt" in text)
check("relation is consensus field", 'leader["relation"]' in text and 'follower["relation"]' in text)
check("time kinds are consensus fields", 'leader["left_time_kind"]' in text and 'follower["left_time_kind"]' in text)
check("event/publication distinction documented", "Publication time is NOT automatically event time" in text)
check("untrusted source boundary present", "UNTRUSTED SOURCE" in text)
check("HTTPS source guard present", 'text.startswith("https://")' in text)
check("localhost blocked", '"localhost"' in text)
check("event hashes present", "event_definition_hash" in text)
check("timeline hash present", "timeline_definition_hash" in text)
check("timeline sealing present", "def seal_timeline" in text)
check("cycle check present", "_has_before_path_id" in text)
check("graph conflict state present", "REL_GRAPH_CONFLICT" in text)
check("transitive path query present", "def get_before_path" in text)
check("pair finalization present", "pair_finalized" in text)
check("bounded events", bool(re.search(r"^MAX_EVENTS\s*=\s*16$", text, re.MULTILINE)))
check("bounded sources", bool(re.search(r"^MAX_SOURCES\s*=\s*4$", text, re.MULTILINE)))
check("no payable surface", ".payable" not in text)
check("no value transfer", "emit(value=" not in text and "send_value" not in text)
check("README says no frontend", "no frontend" in readme.lower())
check("README explains transitive value", "without another web fetch or LLM call" in readme)
check("submission documents deterministic graph", "deterministic" in submission.lower())
check("threat model exists", (ROOT / "docs" / "THREAT_MODEL.md").exists())
check("deployment checklist exists", (ROOT / "docs" / "DEPLOYMENT.md").exists())

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {name}")

print(f"\n{len(checks) - len(failed)}/{len(checks)} preflight checks passed")
if failed:
    sys.exit(1)
