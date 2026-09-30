# Repository handoff

## What this repository is

`fastmcp-prefab-registry-catalog` is a small, portable local catalog for describing the things in an agent environment: agents, skills, policies, resources, machines, databases, projects, and playbooks.

It is not a general platform, graph database, admin SaaS dashboard, workflow engine, or agent runtime.

## What was done

- Inspected related work before implementation. The existing `/Users/bencharney/my-catalog` project is a separate Node/EventCatalog/PDS projection and was not modified.
- Verified current FastMCP Apps/Prefab documentation and installed package APIs.
- Created a generic Pydantic model with sensible defaults, source/interface semantics, and extensible extra fields.
- Implemented recursive YAML loading from a configurable registry root.
- Registry-root precedence is explicit `Registry(root)`, `REGISTRY_ROOT`, then the source-checkout `registry/` fallback.
- Kept registry YAML external to the Python distribution; setuptools explicitly packages `app` only.
- Implemented list, get, search, kind/status filtering, outgoing relationship resolution, incoming/reverse relationship resolution, duplicate-ID checks, and broken-reference checks.
- Added 16 seed/example records; each now records its catalog YAML source authority, and selected objects have explicitly declared (not live) interfaces.
- Exposed FastMCP tools for registry operations plus `skill_discovery_status`, deterministic `catalog`, and the native Generative UI provider tools.
- Exposed a complete merged-catalog resource and an individual object resource template.
- Added optional `SKILLS_ROOTS` discovery through FastMCP `SkillsDirectoryProvider`; discovered `SKILL.md` files and manifests become real MCP resources and runtime catalog objects.
- Added a compact Prefab catalog with real kind/status filters, full-object search indexing, source/interface metadata, resolved machine display names, status badges, pagination, and expandable outgoing/incoming relationship details.
- Added unit tests plus a real-browser GitHub Actions job that launches `fastmcp dev apps` and verifies the rendered app in Chromium.

## Verification baseline

Initial local v0 verification recorded:
- FastMCP Apps dev UI HTTP 200
- FastMCP Inspector HTTP 200
- Playwright screenshots: `catalog-app.png`, `catalog-app-full.png`

Stage 1 packaging/root work was verified and merged in PR #2:
- editable install succeeds on Python 3.12
- 11 pytest tests passed at that stage
- Python compile step passed
- configured, explicit, default, and missing-root behaviors are covered by tests

Stage 2 catalog UX work on `feat/stage2-catalog-ux` is verified by GitHub Actions run `36651211510`:
- test job: success
- 16 pytest tests passed
- Python compile step passed
- Chromium installed and FastMCP Apps preview launched
- browser verification passed kind filtering, status filtering, stable-ID/full-object search, and policy-view rendering
- browser log receipt: `BROWSER_VERIFY succeeded: kind filter, status filter, full-object ID search, and policy view rendered`

Stage 3 source/interface work on `feat/stage3-source-interface-model` is verified by GitHub Actions run `36652704412`:
- 20 pytest tests passed
- compile passed
- browser verification passed source-URI and declared-interface search
- all 16 seed records retain catalog authority; no declared interface is marked available

Do not treat a declared interface as a live connection. Do not treat a local-only test result or a successful write receipt as repository-wide verification; read back the branch/PR head checks.

## Important compatibility note

FastMCP Apps and Prefab are changing quickly. `pyproject.toml` pins `fastmcp[apps]` to `4.0.10` and `prefab-ui` to `0.20.2`. Review the current FastMCP Apps documentation before upgrading either dependency.

The project-local FastMCP binary must be used. A globally resolved older FastMCP CLI caused an internal `--no-reload` incompatibility during initial development.

## Safe change procedure

1. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/NEXT.md`.
2. Preserve the configured YAML → registry → FastMCP → Prefab separation.
3. Make the smallest change.
4. Run the registry and UI tests.
5. If changing packaging, read back GitHub Actions.
6. If changing FastMCP or UI code, require the browser job to pass.
7. Update documentation and `progress.md` with fresh evidence.

## Current limitations

- Live provider binding exists for configured directory-backed skills; other source/interface entries remain descriptive.
- No editing or CRUD.
- No SQLite or other persistence provider.
- No discovery of files, MCP servers, machines, or live status.
- No agent invocation or policy evaluation.
- No JEv routing.
- No graph visualization.
- No authentication.

## Real skill discovery verification

Stage 6 verification covers:
- real directory-backed `SKILL.md` fixtures;
- stable runtime catalog IDs and overlay behavior;
- actual `skill://.../SKILL.md` and manifest resources over FastMCP HTTP;
- runtime projection through `/api/catalog`;
- rendered Prefab catalog behavior;
- coexistence with the existing Generative UI workspace surface.

A discovered skill's `mcp-resource` interface is marked `available` only after provider discovery in the running process. The separate standardized Skills protocol extension is not enabled here.
