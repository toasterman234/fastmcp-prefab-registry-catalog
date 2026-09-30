from __future__ import annotations

from typing import Any

from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Column,
    DataTable,
    DataTableColumn,
    ExpandableRow,
    Heading,
    Row,
    Separator,
    Text,
)

from app.models import RegistryObject


def _status_variant(status: str) -> str:
    return {
        "active": "success",
        "healthy": "success",
        "planned": "info",
        "deprecated": "warning",
        "offline": "destructive",
    }.get(status.casefold(), "secondary")


def _location(obj: RegistryObject) -> str:
    if obj.location and obj.location.machine:
        return obj.location.machine
    return "-"


def _detail_view(obj: RegistryObject) -> Column:
    relationship_lines = [
        f"{relation} → {target}"
        for relation, targets in obj.relationships.items()
        for target in targets
    ] or ["None"]
    return Column(
        gap=1,
        css_class="p-3 text-sm bg-muted/30 rounded-md",
        children=[
            Text(f"ID: {obj.id}"),
            Text(f"Kind: {obj.kind}"),
            Text(f"Description: {obj.description}"),
            Text(f"Status: {obj.status}"),
            Text(f"Capabilities: {', '.join(obj.capabilities) or 'None'}"),
            Text(f"Location: {_location(obj)}"),
            Text(f"Metadata: {obj.metadata or 'None'}"),
            Text("Relationships:"),
            *[Text(f"  {line}") for line in relationship_lines],
        ],
    )


def build_catalog_app(objects: list[RegistryObject], status_summary: str) -> PrefabApp:
    rows: list[dict[str, Any]] = []
    for obj in objects:
        row = {
            "type": obj.kind.title(),
            "name": obj.name,
            "status": Badge(obj.status, variant=_status_variant(obj.status)),
            "description": obj.description,
            "location": _location(obj),
        }
        rows.append(ExpandableRow(row, detail=_detail_view(obj)))

    kind_counts: dict[str, int] = {}
    for obj in objects:
        kind_counts[obj.kind] = kind_counts.get(obj.kind, 0) + 1
    filters = " · ".join(["Everything"] + [f"{kind.title()} ({count})" for kind, count in sorted(kind_counts.items())])

    with PrefabApp(title="Environment Catalog", mode="light") as app:
        with Column(gap=4, css_class="p-4 sm:p-6 max-w-screen-2xl mx-auto"):
            with Row(gap=4, align="center", css_class="flex-wrap"):
                with Column(gap=1, css_class="flex-1 min-w-64"):
                    Heading("Environment Catalog")
                    Text(f"{len(objects)} objects · {status_summary}", css_class="text-sm text-muted-foreground")
                Text("YAML-backed v0 registry", css_class="text-sm text-muted-foreground")
            Separator()
            Text("Kinds: " + filters, css_class="text-sm")
            Text("Use the table search to find by type, name, description, capability, ID, or relationship.", css_class="text-sm text-muted-foreground")
            DataTable(
                columns=[
                    DataTableColumn(key="type", header="Type", sortable=True),
                    DataTableColumn(key="name", header="Name", sortable=True),
                    DataTableColumn(key="status", header="Status", sortable=True),
                    DataTableColumn(key="description", header="Description", sortable=True),
                    DataTableColumn(key="location", header="Host / location", sortable=True),
                ],
                rows=rows,
                search=True,
                paginated=True,
                pageSize=12,
            )
            Separator()
            Heading("Object details", level=2)
            Text("The MCP registry_get and registry_related tools expose complete details and resolved relationships for any selected ID.", css_class="text-sm text-muted-foreground")

    return app
