from __future__ import annotations

from pathlib import Path

from app.models import RegistryObject
from app.registry import Registry


ROOT = Path(__file__).resolve().parents[1] / "registry"


def test_seed_yaml_loads_and_validates() -> None:
    registry = Registry(ROOT)
    report = registry.validate_registry()
    assert report.valid
    assert report.object_count == 16
    assert {obj.kind for obj in registry.list_objects()} == {
        "agent", "skill", "policy", "resource", "machine", "database", "project", "playbook"
    }


def test_search_matches_names_descriptions_and_relationship_targets() -> None:
    registry = Registry(ROOT)
    assert {obj.id for obj in registry.search_objects("root cause")} == {
        "skill.root-cause-analysis",
        "playbook.root-cause-analysis",
    }
    assert {obj.id for obj in registry.search_objects("machine.mac-mini")} == {
        "agent.pi.mac",
        "agent.codex.mac",
        "machine.mac-mini",
    }


def test_filters_are_case_insensitive() -> None:
    registry = Registry(ROOT)
    assert len(registry.filter_objects(kind="AGENT")) == 2
    assert len(registry.filter_objects(status="ACTIVE")) == 16
    assert registry.filter_objects(kind="agent", status="missing") == []


def test_relationships_resolve_to_objects() -> None:
    registry = Registry(ROOT)
    related = registry.related_objects("agent.pi.mac")
    assert {obj.id for obj in related["runs_on"]} == {"machine.mac-mini"}
    assert {obj.id for obj in related["governed_by"]} == {
        "policy.browser-verification-required",
        "policy.evidence-before-completion",
    }


def test_missing_relationship_reference_is_reported(tmp_path: Path) -> None:
    (tmp_path / "broken.yaml").write_text(
        "id: agent.broken\nkind: agent\nname: Broken\nrelationships:\n  uses: [skill.missing]\n",
        encoding="utf-8",
    )
    report = Registry(tmp_path).validate_registry()
    assert not report.valid
    assert any("skill.missing" in issue.message for issue in report.issues)


def test_duplicate_ids_are_reported(tmp_path: Path) -> None:
    record = "id: thing.same\nkind: resource\nname: Same\n"
    (tmp_path / "one.yaml").write_text(record, encoding="utf-8")
    (tmp_path / "two.yaml").write_text(record, encoding="utf-8")
    report = Registry(tmp_path).validate_registry()
    assert not report.valid
    assert any("Duplicate object ID" in issue.message for issue in report.issues)


def test_optional_fields_have_defaults() -> None:
    obj = RegistryObject(id="thing.example", kind="example", name="Example")
    assert obj.status == "active"
    assert obj.capabilities == []
    assert obj.relationships == {}
    assert obj.metadata == {}
