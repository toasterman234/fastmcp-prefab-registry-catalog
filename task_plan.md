# Task Plan: FastMCP Prefab Registry Catalog

## Goal
Build a minimal portable YAML-backed registry/catalog in Python with a domain registry library, FastMCP tools/resources, and a Prefab catalog app.

## Initial v0 phases

### Phase 1: Reconnaissance and API verification
- [x] Inspect target and related existing work
- [x] Verify current FastMCP Apps/Prefab APIs from authoritative docs
- [x] Record architecture findings
- **Status:** complete

### Phase 2: Registry foundation and seed data
- [x] Create Pydantic models and YAML loader
- [x] Add seed records by kind
- [x] Implement registry operations and validation
- [x] Add unit tests
- **Status:** complete

### Phase 3: FastMCP interface
- [x] Add tools
- [x] Add readable object resources
- [x] Add server entrypoint
- [x] Add MCP discovery checks
- **Status:** complete

### Phase 4: Prefab catalog UI
- [x] Implement catalog app tool using Prefab
- [x] Verify app rendering and interaction
- **Status:** complete

### Phase 5: Documentation and final verification
- [x] Write README.md, docs/ARCHITECTURE.md, docs/NEXT.md
- [x] Run tests and app/inspector commands
- [x] Record verified evidence and remaining gaps
- **Status:** complete

## Post-v0 evolution — issue #1

### Stage 1: Packaging/CI + configurable registry root
- [x] Fix setuptools discovery
- [x] Keep YAML external to the Python package
- [x] Add `REGISTRY_ROOT` and explicit-root precedence
- [x] Verify CI install/tests/compile
- **Status:** merged in PR #2

### Stage 2: Catalog UX correctness
- [x] Add real kind filters
- [x] Add real status filters
- [x] Make UI search semantics accurate and full-object
- [x] Resolve machine display names
- [x] Add reverse/incoming relationships
- [x] Add a real Chromium browser smoke test
- **Status:** implemented and verified on `feat/stage2-catalog-ux`; pending merge

### Stage 3: Source/interface model
- [ ] Add small generic source/interface metadata
- [ ] Define authority and refresh/sync semantics
- **Status:** not started

Later stages (skills discovery, MCP federation, files/docs discovery, controlled CRUD, live adapters, JEv/scale features) remain tracked in issue #1 and are intentionally not started.

## Decisions Made
| # | Decision | Rationale |
|---|---|---|
| 1 | New project lives at `fastmcp-prefab-registry-catalog` | User selected isolated directory rather than existing EventCatalog project |
| 2 | YAML remains the durable source of truth | Explicit v0 architecture constraint |
| 3 | UI behavior is browser-verified in target-repo CI | Prevent UI completion claims from depending on static component construction or the currently quota-degraded external Mac artifact path |

## Errors Encountered
| # | Attempts | Error | Resolution |
|---|---|---|---|
| 1 | 1 | Initial tests expected 15 records and a single search result, but the requested seed set contains 16 records and both agents run on the Mac Mini. | Corrected test expectations; implementation behavior was correct. |
| 2 | 1 | Prefab rejected tab state names containing hyphens because state keys must be identifier-safe. | Switched catalog state keys to underscore-safe identifiers and added UI construction coverage. |
