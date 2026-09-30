from __future__ import annotations

import asyncio
import os
from pathlib import Path

from app.catalog import CatalogView
from app.registry import Registry
from app.skill_discovery import (
    build_skills_provider,
    discovery_status,
    project_discovered_skills,
    resolve_skill_roots,
)

ROOT = Path(__file__).resolve().parents[1] / "registry"
FIXTURE_SKILLS = Path(__file__).resolve().parent / "fixtures" / "skills"


def test_resolve_skill_roots_uses_os_pathsep_and_deduplicates(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    raw = os.pathsep.join([str(first), str(second), str(first)])
    assert resolve_skill_roots(raw) == [first.resolve(), second.resolve()]


def test_fastmcp_provider_exposes_real_skill_resources() -> None:
    provider = build_skills_provider([FIXTURE_SKILLS], reload=False)
    assert provider is not None

    resources = asyncio.run(provider.list_resources())
    uris = {str(resource.uri) for resource in resources}

    assert "skill://browser-verification/SKILL.md" in uris
    assert "skill://browser-verification/_manifest" in uris
    assert "skill://discovered-test/SKILL.md" in uris
    assert "skill://discovered-test/_manifest" in uris


def test_discovery_overlays_existing_skill_and_preserves_catalog_annotations() -> None:
    base = Registry(ROOT).list_objects()
    projected = project_discovered_skills([FIXTURE_SKILLS], base)
    view = CatalogView(base, projected)

    skill = view.get_object("skill.browser-verification")
    assert skill is not None
    assert skill.source is not None
    assert skill.source.type == "skill-directory"
    assert skill.source.authority == "external"
    assert skill.source.refresh == "on-read"
    assert skill.source.writeback == "none"
    assert {"browser", "verification"} <= set(skill.capabilities)
    assert skill.metadata["discovery"]["provider"] == "SkillsDirectoryProvider"
    assert any(
        interface.uri == "skill://browser-verification/SKILL.md"
        and interface.status == "available"
        for interface in skill.interfaces
    )
    assert skill.metadata["catalog_source"]["authority"] == "catalog"


def test_discovery_adds_new_skill_with_stable_id() -> None:
    base = Registry(ROOT).list_objects()
    projected = project_discovered_skills([FIXTURE_SKILLS], base)
    view = CatalogView(base, projected)

    skill = view.get_object("skill.discovered-test")
    assert skill is not None
    assert skill.name == "Discovered Test"
    assert skill.source is not None
    assert skill.source.authority == "external"
    assert len(view.list_objects()) == 17


def test_discovered_skill_is_searchable_by_mcp_resource_uri() -> None:
    base = Registry(ROOT).list_objects()
    projected = project_discovered_skills([FIXTURE_SKILLS], base)
    view = CatalogView(base, projected)

    assert {obj.id for obj in view.search_objects("skill://discovered-test/SKILL.md")} == {
        "skill.discovered-test"
    }


def test_discovery_status_reports_missing_roots(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    status = discovery_status([missing], [])
    assert status["enabled"] is True
    assert status["discovered_count"] == 0
    assert status["missing_roots"] == [str(missing)]
