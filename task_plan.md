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
- **Status:** merged in PR #3

### Stage 3: Source/interface model
- [x] Add small generic source/interface metadata
- [x] Define authority, refresh, and writeback semantics
- [x] Add declared interface status/operations
- [x] Project source/interfaces into search and Prefab details
- [x] Verify source/interface discovery in Chromium
- **Status:** promoted to `master` through the integration PRs

### Stage 4: Workspace shell separation — issue #5
- [x] Add a separate Next.js workspace shell
- [x] Keep YAML/domain state out of the shell
- [x] Add read-only FastMCP HTTP catalog projection
- [x] Add Catalog + inspector surface
- [x] Add an Apps surface for the existing Prefab host
- [x] Add explicit Artifacts, Runs, and Review destinations without fake backing models
- [x] Add web build to CI
- [x] Read back CI green for the stacked PR
- **Status:** promoted to `master` through PR #7/#8

### Stage 5: FastMCP Generative UI — issue #9
- [x] Mount native `GenerativeUI()` provider
- [x] Verify `generate_prefab_ui` and `search_prefab_components` registration
- [x] Separate Catalog and Generative UI inside the Apps workspace
- [x] Add real-browser verification of the Apps switcher
- [x] Read back CI green
- **Status:** merged in PR #10

### Stage 6: Real skill discovery
- [x] Discover real `SKILL.md` directories through FastMCP `SkillsDirectoryProvider`
- [x] Expose main files, manifests, and supporting-file templates as MCP resources
- [x] Preserve stable `skill.<directory-name>` IDs
- [x] Overlay matching catalog skills without losing capabilities/relationships
- [x] Distinguish declared from runtime-available interfaces
- [x] Project discovered skills through tools/resources, `/api/catalog`, Prefab, and workspace shell
- [x] Verify real skill resources over FastMCP HTTP
- **Status:** merged in PR #11

### Stage 7: MCP federation
- [x] Opt in catalog objects with `adapter: fastmcp-proxy`
- [x] Support HTTP(S) and local-file MCP targets
- [x] Mount upstream servers with unique namespaces
- [x] Discover upstream tools/resources/resource templates/prompts
- [x] Cache discovery and provide explicit refresh/read-back
- [x] Project connectivity and component evidence onto the same catalog object
- [x] Mark runtime interfaces `available` or `unavailable` without mutating YAML
- [x] Verify a real proxied MCP tool call
- [x] Verify live federation in Prefab, `/api/catalog`, and workspace shell
- **Status:** merged in PR #12


### Stage 8: mcp-use Inspector evaluation/integration
- [ ] Run a compatibility spike against the current FastMCP server before changing code
- [ ] Verify registry tools/resources, Prefab catalog app, Generative UI, skills, and federated MCP components
- [ ] Record reconnect/error behavior and an unavailable-upstream case
- [ ] Add only the smallest reproducible launch/integration wrapper if the spike passes
- [ ] Classify generic workspace responsibilities as delegated to mcp-use vs retained in `web/`
- [ ] Make an explicit adoption decision before removing or simplifying the existing workspace shell
- **Status:** planned on `plan/mcp-use-inspector-integration`; implementation not started

Next is files/docs/policies discovery. Controlled CRUD, broader live adapters, and JEv/scale features remain tracked in issue #1 and are intentionally not started.

## Decisions Made
| # | Decision | Rationale |
|---|---|---|
| 1 | New project lives at `fastmcp-prefab-registry-catalog` | User selected isolated directory rather than existing EventCatalog project |
| 2 | YAML remains the durable source of truth | Explicit v0 architecture constraint |
| 3 | UI behavior is browser-verified in target-repo CI | Prevent UI completion claims from depending on static component construction or the currently quota-degraded external Mac artifact path |
| 4 | Declared interfaces are descriptive until runtime-verified | Prevent catalog metadata from being mistaken for live connectivity |
| 5 | Current seed YAML remains `authority: catalog` | The v0 registry is still the actual source of truth; live external authority is deferred |
| 6 | Workspace shell is separate from Prefab | Navigation/layout should not depend on the FastMCP Apps development host; Prefab remains an app surface |
| 7 | Evaluate mcp-use as a replaceable thin MCP host before integrating it | Generic MCP navigation/hosting should be delegated only if compatibility is proven; domain/catalog/federation authority stays in this repo |

## Errors Encountered
| # | Attempts | Error | Resolution |
|---|---|---|---|
| 1 | 1 | Initial tests expected 15 records and a single search result, but the requested seed set contains 16 records and both agents run on the Mac Mini. | Corrected test expectations; implementation behavior was correct. |
| 2 | 1 | Prefab rejected tab state names containing hyphens because state keys must be identifier-safe. | Switched catalog state keys to underscore-safe identifiers and added UI construction coverage. |

Additional decisions:
- Runtime skill identity is `skill.<directory-name>`.
- A skill's `mcp-resource` interface becomes `available` only after provider discovery.
- Real skill discovery is read-only; it does not install/edit/delete/sync skills.
- MCP federation uses existing catalog interface records, not a second registry.
- Only `adapter: fastmcp-proxy` is executable; descriptive `mcp://` records remain inert.
- Namespace collisions are treated as configuration errors rather than silently shadowing components.
- Runtime federation discovery is cached and read-only; no credentials, mutation, or automatic network scanning are added.
