from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "chronicle.py"


def source():
    return CONTRACT.read_text(encoding="utf-8")


def test_contract_parses_as_python():
    ast.parse(source())


def test_contract_is_contract_only_primitive():
    text = source()
    assert "class Chronicle(gl.Contract)" in text
    assert "@gl.contract_interface" in text
    assert "class IChronicle" in text


def test_consensus_reobserves_evidence():
    text = source()
    assert "gl.vm.run_nondet_unsafe(observe, validate)" in text
    assert "gl.nondet.web.request" in text
    assert "follower = observe()" in text
    assert 'leader["relation"]' in text
    assert 'follower["relation"]' in text


def test_graph_mutation_is_outside_nondet_observer():
    text = source()
    observe_start = text.index("        def observe() -> dict:")
    validate_end = text.index("        return gl.vm.run_nondet_unsafe(observe, validate)", observe_start)
    nondet_block = text[observe_start:validate_end]
    assert "before_edges[" not in nondet_block
    assert "pair_finalized[" not in nondet_block
    assert "relations.get_or_insert_default" not in nondet_block


def test_cycle_guard_and_transitive_path_are_present():
    text = source()
    assert "_has_before_path_id" in text
    assert "REL_GRAPH_CONFLICT" in text
    assert "_find_before_path" in text
    assert "get_before_path" in text


def test_evidence_definitions_are_hash_pinned():
    text = source()
    assert "event_definition_hash" in text
    assert "timeline_definition_hash" in text
    assert "left_event_hash" in text
    assert "right_event_hash" in text
    assert "timeline_hash" in text


def test_prompt_explicitly_separates_publication_and_event_time():
    text = source()
    assert "Publication time is NOT automatically event time" in text
    assert "EVENT_TIME" in text
    assert "PUBLICATION_TIME" in text
    assert "REPORTED_TIME" in text
    assert "OBSERVED_TIME" in text


def test_no_payable_or_value_transfer_surface():
    text = source()
    assert ".payable" not in text
    assert "send_value" not in text
    assert "emit(value=" not in text


def test_url_guard_requires_https_and_blocks_localhost():
    text = source()
    assert 'text.startswith("https://")' in text
    assert '"localhost"' in text
    assert 'host.startswith("127.")' in text
    assert 'host.startswith("10.")' in text


def test_bounded_surface_constants_exist():
    text = source()
    for name in ("MAX_EVENTS", "MAX_SOURCES", "MAX_SOURCE_CHARS", "MAX_EVENT_DEFINITION_LEN", "MAX_EVIDENCE_LEN"):
        assert re.search(rf"^{name}\s*=", text, re.MULTILINE)


def test_consensus_binds_source_availability_and_support():
    text = source()
    assert 'leader["left_available_sources"]' in text
    assert 'follower["left_available_sources"]' in text
    assert "INSUFFICIENT_TEMPORAL_SUPPORT" in text


def test_primitive_strategy_document_exists():
    assert (ROOT / "docs" / "WHY_CHRONICLE_IS_A_PRIMITIVE.md").exists()
