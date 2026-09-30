# Agent handoff guide

This repository is a minimal local registry/catalog built with Python, FastMCP, and Prefab.

## Current state

- v0 remains read-only.
- YAML files are the durable source of truth; the runtime root is explicit `Registry(root)`, then `REGISTRY_ROOT`, then the source-checkout `registry/` fallback.
- `app/registry.py` is the framework-independent domain layer.
- `app/server.py` exposes FastMCP tools/resources and the `catalog()` Prefab app tool.
- `app/ui.py` owns presentation only.
- Seed records are examples and are marked with `metadata.seed: true` and `metadata.example: true`.
- Current seed count is 16 records across 8 kinds.
- The Python distribution packages `app` only; registry YAML is intentionally external operational data.
- The catalog UI has real kind/status filters, full-object search indexing, resolved host names, and expandable outgoing/incoming relationships.
- CI includes a real Chromium smoke check against the rendered FastMCP Prefab app.

## Architecture invariant

Preserve this separation:

```text
Configured YAML registry → Python registry library → FastMCP (resources/tools/Prefab App) → catalog UI
```

Do not move YAML loading into FastMCP handlers, do not make Prefab the data store, and do not add a database or broad platform layer without an explicit architecture decision.

## Layout

| Path | Responsibility |
|---|---|
| `registry/<kind>/*.yaml` | Development/default durable records grouped by kind |
| `app/models.py` | Generic Pydantic schema and validation report models |
| `app/registry.py` | Root resolution, load, list, get, search, filter, outgoing/incoming relationships, validation |
| `app/server.py` | FastMCP server, tools, resources, `catalog()` |
| `app/ui.py` | Prefab catalog composition |
| `tests/test_registry.py` | Registry behavior, relationship direction, and registry-root tests |
| `tests/test_ui.py` | UI helper/catalog-construction tests |
| `scripts/verify_catalog_ui.py` | Playwright browser verification against `fastmcp dev apps` |
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

For local browser verification:

```bash
.venv/bin/python -m pip install -e '.[test,ui-test]'
.venv/bin/python -m playwright install chromium
```

For a registry outside the source checkout:

```bash
export REGISTRY_ROOT=/path/to/environment-registry
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

1. `python -m pip install -e '.[test]'` succeeds in a clean environment.
2. `.venv/bin/python -m pytest -q`
3. MCP discovery finds the seven expected tools and registry resources.
4. `registry_validate` reports valid YAML, no duplicate IDs, and no broken relationship references.
5. UI changes pass the real-browser job in `.github/workflows/test.yml`.
6. GitHub Actions is read back green for the branch/PR head being claimed.

## Intentional non-goals

Do not implement the items in `docs/NEXT.md` unless the task explicitly scopes one of them.
