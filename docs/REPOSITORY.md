# Repository handoff

## What this repository is

`fastmcp-prefab-registry-catalog` is a small, portable local catalog for describing the things in an agent environment: agents, skills, policies, resources, machines, databases, projects, and playbooks.

It is not a general platform, graph database, admin SaaS dashboard, workflow engine, or agent runtime.

## What was done

- Inspected related work before implementation. The existing `/Users/bencharney/my-catalog` project is a separate Node/EventCatalog/PDS projection and was not modified.
- Verified current FastMCP Apps/Prefab documentation and installed package APIs.
- Created a generic Pydantic model with sensible defaults and extensible extra fields.
- Implemented recursive YAML loading from a configurable registry root.
- Registry-root precedence is explicit `Registry(root)`, `REGISTRY_ROOT`, then the source-checkout `registry/` fallback.
- Kept registry YAML external to the Python distribution; setuptools explicitly packages `app` only.
- Implemented list, get, search, kind/status filtering, relationship resolution, duplicate-ID checks, and broken-reference checks.
- Added 16 seed/example records.
- Exposed FastMCP tools: `registry_search`, `registry_get`, `registry_list`, `registry_related`, `registry_validate`, and `catalog`.
- Exposed a complete registry resource and an individual object resource template.
- Added a compact Prefab data table with search, pagination, status badges, expandable details, and relationship text.
- Added unit tests and local browser/MCP verification evidence.

## Verification baseline

Initial local v0 verification recorded:
- FastMCP Apps dev UI HTTP 200
- FastMCP Inspector HTTP 200
- Playwright screenshots: `catalog-app.png`, `catalog-app-full.png`

Stage 1 packaging/root work on `fix/stage1-ci-registry-root` was verified in GitHub Actions:
- editable install succeeds on Python 3.12
- 11 pytest tests pass
- Python compile step passes
- configured, explicit, default, and missing-root behaviors are covered by tests

Do not treat a local-only test result as repository-wide verification when GitHub Actions is red.

## Important compatibility note

FastMCP Apps and Prefab are changing quickly. `pyproject.toml` pins `fastmcp[apps]` to `4.0.10` and `prefab-ui` to `0.20.2`. Review the current FastMCP Apps documentation before upgrading either dependency.

The project-local FastMCP binary must be used. A globally resolved older FastMCP CLI caused an internal `--no-reload` incompatibility during development.

## Safe change procedure

1. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/NEXT.md`.
2. Preserve the configured YAML → registry → FastMCP → Prefab separation.
3. Make the smallest change.
4. Run the registry tests and validation.
5. If changing packaging, read back GitHub Actions.
6. If changing FastMCP or UI code, run discovery and launch the Apps dev UI.
7. Update documentation and `progress.md` with fresh evidence.

## Current limitations

- No editing or CRUD.
- No SQLite or other persistence provider.
- No discovery of files, MCP servers, machines, or live status.
- No agent invocation or policy evaluation.
- No JEv routing.
- No graph visualization.
- No authentication.
