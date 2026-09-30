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
- The catalog UI has real kind/status filters, full-object search indexing, resolved host names, source metadata, declared interfaces, and expandable outgoing/incoming relationships.
- Every seed record declares its YAML catalog source as authoritative by default. Runtime-discovered skills may overlay matching skill records with `authority: external` and an `available` MCP resource interface after FastMCP discovery succeeds.
- `SKILLS_ROOTS` enables real directory-backed skill discovery. No configured roots means no runtime skill projection.
- MCP federation is opt-in through catalog interfaces with `type: mcp` and `adapter: fastmcp-proxy`; other MCP-looking interfaces remain descriptive only.
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
| `app/models.py` | Generic Pydantic schema, source/interface semantics, and validation report models |
| `app/registry.py` | Durable YAML registry loading and validation |
| `app/catalog.py` | Read-only merged catalog view over durable records plus runtime projections |
| `app/skill_discovery.py` | FastMCP skill-root configuration, provider creation, and runtime skill projection |
| `app/mcp_federation.py` | Catalog-to-proxy bindings, namespaced mounts, upstream discovery/cache, and runtime MCP overlays |
| `app/server.py` | FastMCP server, tools, resources, `catalog()` |
| `app/ui.py` | Prefab catalog composition |
| `tests/test_registry.py` | Registry behavior, relationship direction, and registry-root tests |
| `tests/test_ui.py` | UI helper/catalog-construction tests |
| `tests/test_skills.py` | Real `SkillsDirectoryProvider` resource/projection tests |
| `tests/test_mcp_federation.py` | Real subprocess MCP proxy/discovery/tool-call tests |
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

Use a globally unique ID and relationship target IDs. New kinds need only a new directory and YAML records; no Python dispatch is required.

When adding `source` or `interfaces`:
- do not mark an interface `available` unless runtime connectivity has actually been verified
- use `authority: catalog` while the YAML record is authoritative
- use `external` only when an external source is the real authority
- keep writeback `controlled` or `none` until a mutation path is explicitly implemented

Run tests and registry validation after changes.

## Before claiming completion

Verify:

1. `python -m pip install -e '.[test]'` succeeds in a clean environment.
2. `.venv/bin/python -m pytest -q`
3. MCP discovery finds the eleven expected registry/skill/federation/Generative UI tools; configured skills and federated MCP servers expose their additional resources/tools through providers.
4. `registry_validate` reports valid YAML, no duplicate IDs, and no broken relationship references.
5. UI/provider changes pass the real-browser job, live MCP federation projection check, workspace Apps check, HTTP catalog projection check, and skill-resource check in `.github/workflows/test.yml`.
6. GitHub Actions is read back green for the branch/PR head being claimed.

## Intentional non-goals

Do not implement the items in `docs/NEXT.md` unless the task explicitly scopes one of them.

## Skill discovery

```bash
export SKILLS_ROOTS="/path/to/skills:/another/path/to/skills"
```

Use the platform path separator (`:` on macOS/Linux). Each root contains immediate child skill directories with `SKILL.md`. Do not mark an interface `available` merely because it is configured; the skill projection does so only after the provider discovers the skill.

## MCP federation

Only interfaces with this shape are mounted:

```yaml
- type: mcp
  uri: https://example.internal/mcp  # or file:///absolute/path/server.py
  adapter: fastmcp-proxy
  namespace: example
  status: declared
```

Rules:
- namespaces must be unique and are normalized to MCP-safe names;
- do not encode secrets in `uri`;
- HTTP(S) and `file://` targets are supported in this stage;
- upstream component discovery is cached for 30 seconds;
- use `mcp_federation_status(refresh=true)` for a fresh probe;
- runtime `available` / `unavailable` status is projection evidence only and is never written back to YAML.
