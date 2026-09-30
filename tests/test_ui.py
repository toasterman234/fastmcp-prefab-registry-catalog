from __future__ import annotations

from pathlib import Path

from app.registry import Registry
from app.ui import _kind_plural, _location, _search_blob, _source_label, build_catalog_app


ROOT = Path(__file__).resolve().parents[1] / "registry"


def _fixture():
    registry = Registry(ROOT)
    objects = registry.list_objects()
    by_id = {obj.id: obj for obj in objects}
    incoming = {obj.id: registry.incoming_objects(obj.id) for obj in objects}
    return registry, objects, by_id, incoming


def test_search_blob_includes_nonvisible_registry_fields() -> None:
    _, _, by_id, incoming = _fixture()
    pi = by_id["agent.pi.mac"]

    blob = _search_blob(pi, by_id, incoming)

    assert "agent.pi.mac" in blob
    assert "filesystem" in blob
    assert "browser verification required" in blob
    assert "policy.browser-verification-required" in blob
    assert "mac mini" in blob
    assert "registry://agents/pi.yaml" in blob
    assert "cli://pi" in blob
    assert "controlled" in blob
    assert "example" in blob


def test_source_label_is_compact_and_explicit() -> None:
    _, _, by_id, _ = _fixture()
    assert _source_label(by_id["agent.pi.mac"]) == "registry-yaml · catalog"


def test_kind_pluralization_is_human_readable() -> None:
    assert _kind_plural("agent") == "Agents"
    assert _kind_plural("policy") == "Policies"
    assert _kind_plural("database") == "Databases"


def test_location_resolves_machine_display_name() -> None:
    _, _, by_id, _ = _fixture()
    assert _location(by_id["agent.pi.mac"], by_id) == "Mac Mini"


def test_catalog_app_builds_with_kind_status_source_and_incoming_data() -> None:
    _, objects, _, incoming = _fixture()
    app = build_catalog_app(objects, "active: 16", incoming)
    assert app is not None
