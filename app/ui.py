from __future__ import annotations

import json
import re
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
    Tab,
    Tabs,
    Text,
)

from app.models import InterfaceSpec, RegistryObject

IncomingRelationships = dict[str, dict[str, list[RegistryObject]]]


def _state_key(value: str) -> str:
    suffix = re.sub(r"[^A-Za-z0-9_]", "_", value.casefold())
    return f"catalog_status_{suffix}"


def _kind_plural(kind: str) -> str:
    lower = kind.casefold()
    if lower.endswith("y") and len(kind) > 1 and lower[-2] not in "aeiou":
        return kind[:-1].title() + "ies"
    if lower.endswith("s"):
        return kind.title()
    return kind.title() + "s"


def _status_variant(status: str) -> str:
    return {
        "active": "success",
        "healthy": "success",
        "planned": "info",
        "deprecated": "warning",
        "offline": "destructive",
    }.get(status.casefold(), "secondary")


def _location(obj: RegistryObject, objects_by_id: dict[str, RegistryObject]) -> str:
    if not obj.location or not obj.location.machine:
        return "-"
    machine_id = obj.location.machine
    machine = objects_by_id.get(machine_id)
    return machine.name if machine else machine_id


def _source_label(obj: RegistryObject) -> str:
    if not obj.source:
        return "-"
    return f"{obj.source.type} · {obj.source.authority}"


def _interface_label(interface: InterfaceSpec) -> str:
    parts = [interface.type]
    if interface.adapter:
        parts.append(interface.adapter)
    parts.append(interface.status)
    return " · ".join(parts)


def _display_object(obj: RegistryObject) -> str:
    return f"{obj.name} ({obj.id})"


def _search_blob(
    obj: RegistryObject,
    objects_by_id: dict[str, RegistryObject],
    incoming: IncomingRelationships,
) -> str:
    outgoing_parts: list[str] = []
    for relation, targets in obj.relationships.items():
        outgoing_parts.append(relation)
        for target_id in targets:
            outgoing_parts.append(target_id)
            if target := objects_by_id.get(target_id):
                outgoing_parts.append(target.name)

    incoming_parts: list[str] = []
    for relation, sources in incoming.get(obj.id, {}).items():
        incoming_parts.append(relation)
        for source in sources:
            incoming_parts.extend([source.id, source.name])

    source_parts: list[str] = []
    if obj.source:
        source_parts.extend(
            [
                obj.source.type,
                obj.source.uri,
                obj.source.authority,
                obj.source.refresh,
                obj.source.writeback,
            ]
        )

    interface_parts: list[str] = []
    for interface in obj.interfaces:
        interface_parts.extend(
            [
                interface.type,
                interface.uri or "",
                interface.adapter or "",
                interface.status,
                *interface.operations,
            ]
        )

    values = [
        obj.id,
        obj.kind,
        obj.name,
        obj.description,
        obj.status,
        _location(obj, objects_by_id),
        *obj.capabilities,
        *outgoing_parts,
        *incoming_parts,
        *source_parts,
        *interface_parts,
        json.dumps(obj.metadata, sort_keys=True, default=str),
    ]
    return " ".join(value for value in values if value).casefold()


def _detail_view(
    obj: RegistryObject,
    objects_by_id: dict[str, RegistryObject],
    incoming: IncomingRelationships,
) -> Column:
    outgoing_lines = [
        f"{relation} → {_display_object(target)}"
        for relation, targets in obj.relationships.items()
        for target_id in targets
        if (target := objects_by_id.get(target_id))
    ]
    unresolved_outgoing = [
        f"{relation} → {target_id} (unresolved)"
        for relation, targets in obj.relationships.items()
        for target_id in targets
        if target_id not in objects_by_id
    ]
    incoming_lines = [
        f"{relation} ← {_display_object(source)}"
        for relation, sources in incoming.get(obj.id, {}).items()
        for source in sources
    ]

    source_lines = ["None"]
    if obj.source:
        source_lines = [
            f"Type: {obj.source.type}",
            f"URI: {obj.source.uri}",
            f"Authority: {obj.source.authority}",
            f"Refresh: {obj.source.refresh}",
            f"Writeback: {obj.source.writeback}",
        ]

    interface_lines = [
        (
            f"{_interface_label(interface)}"
            + (f" · {interface.uri}" if interface.uri else "")
            + (f" · operations: {', '.join(interface.operations)}" if interface.operations else "")
        )
        for interface in obj.interfaces
    ] or ["None"]

    return Column(
        gap=2,
        css_class="p-3 text-sm bg-muted/30 rounded-md",
        children=[
            Row(
                gap=2,
                align="center",
                css_class="flex-wrap",
                children=[
                    Badge(obj.kind.title(), variant="secondary"),
                    Badge(obj.status, variant=_status_variant(obj.status)),
                    Text(obj.id, css_class="font-mono text-xs text-muted-foreground"),
                ],
            ),
            Text(obj.description or "No description."),
            Text(
                f"Capabilities: {', '.join(obj.capabilities) or 'None'}",
                css_class="text-muted-foreground",
            ),
            Text(
                f"Host / location: {_location(obj, objects_by_id)}",
                css_class="text-muted-foreground",
            ),
            Separator(),
            Text("Source", css_class="font-medium"),
            *[Text(line) for line in source_lines],
            Text("Declared interfaces", css_class="font-medium pt-1"),
            *[Text(line) for line in interface_lines],
            Separator(),
            Text("Outgoing relationships", css_class="font-medium"),
            *[Text(line) for line in (outgoing_lines + unresolved_outgoing or ["None"])],
            Text("Incoming relationships", css_class="font-medium pt-1"),
            *[Text(line) for line in (incoming_lines or ["None"])],
            Text(
                f"Metadata: {json.dumps(obj.metadata, sort_keys=True, default=str) if obj.metadata else 'None'}",
                css_class="text-xs text-muted-foreground pt-1",
            ),
        ],
    )


def _catalog_table(
    objects: list[RegistryObject],
    objects_by_id: dict[str, RegistryObject],
    incoming: IncomingRelationships,
) -> DataTable | Text:
    if not objects:
        return Text("No objects match these filters.", css_class="text-sm text-muted-foreground")

    rows: list[dict[str, Any] | ExpandableRow] = []
    for obj in objects:
        row = {
            "type": obj.kind.title(),
            "name": obj.name,
            "status": Badge(obj.status, variant=_status_variant(obj.status)),
            "description": obj.description,
            "capabilities": ", ".join(obj.capabilities) or "-",
            "source": _source_label(obj),
            "location": _location(obj, objects_by_id),
            "_search": _search_blob(obj, objects_by_id, incoming),
        }
        rows.append(
            ExpandableRow(
                row,
                detail=_detail_view(obj, objects_by_id, incoming),
            )
        )

    return DataTable(
        columns=[
            DataTableColumn(key="type", header="Type", sortable=True),
            DataTableColumn(key="name", header="Name", sortable=True),
            DataTableColumn(key="status", header="Status", sortable=True),
            DataTableColumn(key="description", header="Description", sortable=True),
            DataTableColumn(
                key="source",
                header="Source",
                sortable=True,
                header_class="hidden lg:table-cell",
                cell_class="hidden lg:table-cell",
            ),
            DataTableColumn(
                key="capabilities",
                header="Capabilities",
                sortable=True,
                header_class="hidden xl:table-cell",
                cell_class="hidden xl:table-cell",
            ),
            DataTableColumn(
                key="location",
                header="Host / location",
                sortable=True,
                header_class="hidden md:table-cell",
                cell_class="hidden md:table-cell",
            ),
            DataTableColumn(
                key="_search",
                header="Search index",
                header_class="hidden",
                cell_class="hidden",
            ),
        ],
        rows=rows,
        search=True,
        paginated=True,
        page_size=12,
    )


def _status_tabs(
    objects: list[RegistryObject],
    objects_by_id: dict[str, RegistryObject],
    incoming: IncomingRelationships,
    state_name: str,
) -> Tabs:
    statuses = sorted({obj.status for obj in objects}, key=str.casefold)
    tabs = [
        Tab(
            f"All ({len(objects)})",
            value="all",
            children=[_catalog_table(objects, objects_by_id, incoming)],
        )
    ]
    for status in statuses:
        filtered = [obj for obj in objects if obj.status.casefold() == status.casefold()]
        tabs.append(
            Tab(
                f"{status.title()} ({len(filtered)})",
                value=status.casefold(),
                children=[_catalog_table(filtered, objects_by_id, incoming)],
            )
        )
    return Tabs(
        name=state_name,
        value="all",
        variant="line",
        children=tabs,
        css_class="w-full",
    )


def build_catalog_app(
    objects: list[RegistryObject],
    status_summary: str,
    incoming: IncomingRelationships | None = None,
) -> PrefabApp:
    incoming = incoming or {}
    objects_by_id = {obj.id: obj for obj in objects}

    kind_tabs = [
        Tab(
            f"Everything ({len(objects)})",
            value="all",
            children=[_status_tabs(objects, objects_by_id, incoming, "catalog_status_all")],
        )
    ]
    for kind in sorted({obj.kind for obj in objects}, key=str.casefold):
        filtered = [obj for obj in objects if obj.kind.casefold() == kind.casefold()]
        kind_tabs.append(
            Tab(
                f"{_kind_plural(kind)} ({len(filtered)})",
                value=kind.casefold(),
                children=[
                    _status_tabs(
                        filtered,
                        objects_by_id,
                        incoming,
                        _state_key(kind),
                    )
                ],
            )
        )

    with PrefabApp(title="Environment Catalog", mode="light") as app:
        with Column(gap=4, css_class="p-4 sm:p-6 max-w-screen-2xl mx-auto"):
            with Row(gap=4, align="center", css_class="flex-wrap"):
                with Column(gap=1, css_class="flex-1 min-w-64"):
                    Heading("Environment Catalog")
                    Text(
                        f"{len(objects)} objects · {status_summary}",
                        css_class="text-sm text-muted-foreground",
                    )
                Text("YAML-backed registry", css_class="text-sm text-muted-foreground")
            Separator()
            Text(
                "Filter by kind, then status. Expand a row for source, declared interfaces, and resolved relationships.",
                css_class="text-sm text-muted-foreground",
            )
            Text(
                "Search covers names, IDs, descriptions, capabilities, sources, interfaces, relationships, metadata, and host/location.",
                css_class="text-sm text-muted-foreground",
            )
            Tabs(
                name="catalog_kind",
                value="all",
                variant="line",
                children=kind_tabs,
                css_class="w-full overflow-x-auto",
            )

    return app
