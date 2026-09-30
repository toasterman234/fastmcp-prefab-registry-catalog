# Repository handoff

## What this repository is

`fastmcp-prefab-registry-catalog` is a small, portable local catalog for describing the things in an agent environment: agents, skills, policies, resources, machines, databases, projects, and playbooks.

It is not a general platform, graph database, admin SaaS dashboard, workflow engine, or agent runtime.

## What was done

- Inspected related work before implementation. The existing `/Users/bencharney/my-catalog` project is a separate Node/EventCatalog/PDS projection and was not modified.
- Verified current FastMCP Apps/Prefab documentation and installed package APIs.
- Created a generic Pydantic model with sensible defaults and extensible extra fields.
- Implemented recursive YAML loading from `registry/`.
- Implemented list, get, search, kind/status filtering, relationship resolution, duplicate-ID checks, and broken-reference checks.
- Added 16 seed/example records.
- Exposed FastMCP tools: `registry_search`, `registry_get`, `registry_list`, `registry_related`, `registry_validate`, and `catalog`.
- Exposed a complete registry resource and an individual object resource template.
- Added a compact Prefab data table with search, pagination, status badges, expandable details, and relationship text.
- Added unit tests and local browser/MCP verification evidence.

## Verification baseline

The last verified baseline was:

- 7 pytest tests passing
- 16 valid loaded objects
- 8 discovered kinds
- 6 discovered FastMCP tools
- `registry://objects` resource discovered
- `registry://objects/{object_id}` resource template discovered
- `registry_validate` returns `valid: true`
- FastMCP Apps dev UI returns HTTP 200
- FastMCP Inspector returns HTTP 200
- Playwright screenshots: `catalog-app.png`, `catalog-app-full.png`

## Important compatibility note

FastMCP Apps and Prefab are changing quickly. `pyproject.toml` pins `fastmcp[apps]` to `4.0.10` and `prefab-ui` to `0.20.2`. Review the current FastMCP Apps documentation before upgrading either dependency.

The project-local FastMCP binary must be used. A globally resolved older FastMCP CLI caused an internal `--no-reload` incompatibility during development.

## Safe change procedure

1. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/NEXT.md`.
2. Preserve the YAML → registry → FastMCP → Prefab separation.
3. Make the smallest change.
4. Run the registry tests and validation.
5. If changing FastMCP or UI code, run discovery and launch the Apps dev UI.
6. Update documentation and `progress.md` with fresh evidence.

## Current limitations

- No editing or CRUD.
- No SQLite or other provider.
- No discovery of files, MCP servers, machines, or live status.
- No agent invocation or policy evaluation.
- No JEv routing.
- No graph visualization.
- No authentication.
