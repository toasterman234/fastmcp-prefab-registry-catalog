from __future__ import annotations

from pathlib import Path

from app.registry import Registry
from app.ui import _location, _search_blob, build_catalog_app


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
    assert "example" in blob


def test_location_resolves_machine_display_name() -> None:
    _, _, by_id, _ = _fixture()
    assert _location(by_id["agent.pi.mac"], by_id) == "Mac Mini"


def test_catalog_app_builds_with_kind_status_and_incoming_data() -> None:
    _, objects, _, incoming = _fixture()
    app = build_catalog_app(objects, "active: 16", incoming)
    assert app is not None
