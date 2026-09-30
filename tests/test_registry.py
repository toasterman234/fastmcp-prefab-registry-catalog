from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError
import pytest

from app.models import RegistryObject, SourceSpec
from app.registry import DEFAULT_REGISTRY_ROOT, Registry


ROOT = Path(__file__).resolve().parents[1] / "registry"


def test_seed_yaml_loads_and_validates() -> None:
    registry = Registry(ROOT)
    report = registry.validate_registry()
    assert report.valid
    assert report.object_count == 16
    assert {obj.kind for obj in registry.list_objects()} == {
        "agent", "skill", "policy", "resource", "machine", "database", "project", "playbook"
    }


def test_seed_records_have_truthful_catalog_sources() -> None:
    registry = Registry(ROOT)
    assert all(obj.source is not None for obj in registry.list_objects())
    assert {obj.source.authority for obj in registry.list_objects() if obj.source} == {"catalog"}
    assert {obj.source.refresh for obj in registry.list_objects() if obj.source} == {"manual"}
    assert {obj.source.writeback for obj in registry.list_objects() if obj.source} == {"controlled"}


def test_declared_interfaces_do_not_imply_live_availability() -> None:
    registry = Registry(ROOT)
    interfaces = [interface for obj in registry.list_objects() for interface in obj.interfaces]
    assert interfaces
    assert {interface.status for interface in interfaces} == {"declared"}


def test_search_matches_names_descriptions_relationships_sources_and_interfaces() -> None:
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
    assert {obj.id for obj in registry.search_objects("cli://pi")} == {"agent.pi.mac"}
    assert {obj.id for obj in registry.search_objects("bolt://neo4j")} == {"database.neo4j"}
    assert "project.master-repo" in {obj.id for obj in registry.search_objects("github")}


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


def test_incoming_relationships_resolve_sources() -> None:
    registry = Registry(ROOT)

    mac_incoming = registry.incoming_objects("machine.mac-mini")
    assert {obj.id for obj in mac_incoming["runs_on"]} == {
        "agent.pi.mac",
        "agent.codex.mac",
    }

    evidence_incoming = registry.incoming_objects("policy.evidence-before-completion")
    assert {obj.id for obj in evidence_incoming["governed_by"]} == {
        "agent.pi.mac",
        "agent.codex.mac",
    }
    assert {obj.id for obj in evidence_incoming["uses"]} == {
        "playbook.root-cause-analysis"
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
    assert obj.source is None
    assert obj.interfaces == []
    assert obj.capabilities == []
    assert obj.relationships == {}
    assert obj.metadata == {}


def test_source_modes_are_bounded() -> None:
    with pytest.raises(ValidationError):
        SourceSpec(
            type="service",
            uri="service://example",
            authority="mystery",
        )


def test_default_registry_root_preserves_source_checkout_behavior(monkeypatch) -> None:
    monkeypatch.delenv("REGISTRY_ROOT", raising=False)
    registry = Registry()
    assert registry.root == DEFAULT_REGISTRY_ROOT == ROOT
    assert registry.validate_registry().valid
    assert len(registry.list_objects()) == 16


def test_registry_root_can_be_configured_from_environment(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "custom.yaml").write_text(
        "id: thing.custom\nkind: resource\nname: Custom\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("REGISTRY_ROOT", str(tmp_path))

    registry = Registry()

    assert registry.root == tmp_path
    assert [obj.id for obj in registry.list_objects()] == ["thing.custom"]
    assert registry.validate_registry().valid


def test_explicit_registry_root_overrides_environment(
    tmp_path: Path, monkeypatch
) -> None:
    environment_root = tmp_path / "environment"
    explicit_root = tmp_path / "explicit"
    environment_root.mkdir()
    explicit_root.mkdir()
    (environment_root / "env.yaml").write_text(
        "id: thing.environment\nkind: resource\nname: Environment\n",
        encoding="utf-8",
    )
    (explicit_root / "explicit.yaml").write_text(
        "id: thing.explicit\nkind: resource\nname: Explicit\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("REGISTRY_ROOT", str(environment_root))

    registry = Registry(explicit_root)

    assert registry.root == explicit_root
    assert [obj.id for obj in registry.list_objects()] == ["thing.explicit"]


def test_missing_configured_registry_root_is_visible(tmp_path: Path, monkeypatch) -> None:
    missing_root = tmp_path / "missing"
    monkeypatch.setenv("REGISTRY_ROOT", str(missing_root))

    report = Registry().validate_registry()

    assert not report.valid
    assert report.object_count == 0
    assert any(
        str(missing_root) in issue.message and "does not exist" in issue.message
        for issue in report.issues
    )
