from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp.server.providers.skills import SkillsDirectoryProvider

from app.models import InterfaceSpec, RegistryObject, SourceSpec

SKILLS_ROOTS_ENV = "SKILLS_ROOTS"


def resolve_skill_roots(value: str | None = None) -> list[Path]:
    """Resolve configured skill roots from an os.pathsep-separated string."""
    raw = os.getenv(SKILLS_ROOTS_ENV, "") if value is None else value
    roots: list[Path] = []
    seen: set[Path] = set()
    for item in raw.split(os.pathsep):
        item = item.strip()
        if not item:
            continue
        path = Path(item).expanduser().resolve()
        if path not in seen:
            roots.append(path)
            seen.add(path)
    return roots


def build_skills_provider(
    roots: list[Path] | None = None,
    *,
    reload: bool = True,
) -> SkillsDirectoryProvider | None:
    roots = resolve_skill_roots() if roots is None else roots
    if not roots:
        return None
    return SkillsDirectoryProvider(
        roots=roots,
        reload=reload,
        supporting_files="template",
    )


def _available_skill_interface(name: str) -> InterfaceSpec:
    return InterfaceSpec(
        type="mcp-resource",
        uri=f"skill://{name}/SKILL.md",
        adapter="fastmcp-skills",
        status="available",
        operations=["read", "manifest", "read-supporting-file"],
    )


def _discovery_metadata(provider_name: str, info: Any) -> dict[str, Any]:
    return {
        "discovered": True,
        "provider": provider_name,
        "skill_name": info.name,
        "file_count": len(info.files),
        "frontmatter": dict(info.frontmatter),
    }


def _merge_interfaces(
    existing: list[InterfaceSpec],
    available: InterfaceSpec,
) -> list[InterfaceSpec]:
    merged = [
        interface
        for interface in existing
        if not (
            interface.type == available.type
            and interface.uri == available.uri
            and interface.adapter == available.adapter
        )
    ]
    merged.append(available)
    return merged


def project_discovered_skills(
    roots: list[Path],
    base_objects: list[RegistryObject],
) -> list[RegistryObject]:
    """Discover skills with FastMCP and project them into catalog objects.

    Stable identity is based on the skill directory name: skill.<directory-name>.
    If that ID already exists in the YAML catalog, semantic annotations from the
    YAML record are retained while runtime source/interface state is refreshed.
    """
    provider = build_skills_provider(roots, reload=False)
    if provider is None:
        return []

    base_by_id = {obj.id: obj for obj in base_objects}
    projected: list[RegistryObject] = []

    for child in provider.providers:
        info = child.skill_info
        object_id = f"skill.{info.name}"
        main_file = (info.path / info.main_file).resolve()
        source = SourceSpec(
            type="skill-directory",
            uri=main_file.as_uri(),
            authority="external",
            refresh="on-read",
            writeback="none",
        )
        available_interface = _available_skill_interface(info.name)
        discovery = _discovery_metadata(type(provider).__name__, info)

        if existing := base_by_id.get(object_id):
            metadata = dict(existing.metadata)
            if existing.source:
                metadata["catalog_source"] = existing.source.model_dump(mode="json")
            metadata["discovery"] = discovery
            projected.append(
                RegistryObject(
                    **{
                        **existing.to_dict(),
                        "description": info.description or existing.description,
                        "source": source,
                        "interfaces": _merge_interfaces(
                            existing.interfaces, available_interface
                        ),
                        "metadata": metadata,
                    }
                )
            )
            continue

        display_name = str(info.frontmatter.get("name") or info.name.replace("-", " ").title())
        projected.append(
            RegistryObject(
                id=object_id,
                kind="skill",
                name=display_name,
                description=info.description,
                status="active",
                source=source,
                interfaces=[available_interface],
                capabilities=[],
                relationships={},
                metadata={"discovery": discovery},
            )
        )

    return projected


def discovery_status(
    roots: list[Path],
    projected: list[RegistryObject],
) -> dict[str, Any]:
    return {
        "enabled": bool(roots),
        "provider": "SkillsDirectoryProvider" if roots else None,
        "roots": [str(root) for root in roots],
        "existing_roots": [str(root) for root in roots if root.exists()],
        "missing_roots": [str(root) for root in roots if not root.exists()],
        "discovered_count": len(projected),
        "discovered_ids": sorted(obj.id for obj in projected),
        "refresh": "on-read" if roots else None,
        "protocol_surface": "mcp-resources" if roots else None,
    }
