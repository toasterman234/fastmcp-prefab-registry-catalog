# Agent handoff guide

This repository is a minimal local registry/catalog built with Python, FastMCP, and Prefab.

## Current state

- v0 is read-only.
- YAML files under `registry/` are the durable source of truth.
- `app/registry.py` is the framework-independent domain layer.
- `app/server.py` exposes FastMCP tools/resources and the `catalog()` Prefab app tool.
- `app/ui.py` owns presentation only.
- Seed records are examples and are marked with `metadata.seed: true` and `metadata.example: true`.
- Current seed count is 16 records across 8 kinds.

## Architecture invariant

Preserve this separation:

```text
YAML registry → Python registry library → FastMCP (resources/tools/Prefab App) → catalog UI
```

Do not move YAML loading into FastMCP handlers, do not make Prefab the data store, and do not add a database or broad platform layer without an explicit architecture decision.

## Layout

| Path | Responsibility |
|---|---|
| `registry/<kind>/*.yaml` | Durable records grouped by kind |
| `app/models.py` | Generic Pydantic schema and validation report models |
| `app/registry.py` | Load, list, get, search, filter, relationships, validation |
| `app/server.py` | FastMCP server, tools, resources, `catalog()` |
| `app/ui.py` | Prefab catalog composition |
| `tests/test_registry.py` | Registry behavior tests |
| `docs/ARCHITECTURE.md` | Responsibility boundaries and data flow |
| `docs/NEXT.md` | Explicitly deferred extensions |
| `findings.md` | API/reconnaissance notes |
| `progress.md` | Session verification log |
| `task_plan.md` | Persistent task plan |

## Commands

Use the project-local environment, not a globally resolved FastMCP CLI:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

FastMCP Apps dev UI:

```bash
env PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp dev apps app/server.py
```

Inspector:

```bash
env PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp dev inspector app/server.py
```

## Adding records

Use a globally unique ID and relationship target IDs. New kinds need only a new directory and YAML records; no Python dispatch is required. Run tests and registry validation after changes.

## Before claiming completion

Verify:

1. `.venv/bin/python -m pytest -q`
2. MCP discovery finds the six expected tools and registry resources.
3. `registry_validate` reports valid YAML, no duplicate IDs, and no broken relationship references.
4. The FastMCP Apps UI launches and is checked in a browser when UI code changes.

## Intentional non-goals

Do not implement the items in `docs/NEXT.md` unless the task explicitly scopes one of them.
