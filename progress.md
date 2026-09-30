# Progress: FastMCP Prefab Registry Catalog

## 2026-09-30

### Initial v0
- Created isolated target directory and initialized persistent planning files.
- Verified current FastMCP Apps/Prefab docs and pinned FastMCP 4.0.10 plus prefab-ui 0.20.2 in the isolated environment.
- Implemented generic Pydantic/YAML registry, 16 seed records, registry operations, FastMCP tools/resources, and Prefab catalog app.
- Initial local tests passed: 7 tests.
- MCP in-process discovery verified: 6 tools, full snapshot resource, object resource template, validation, search, filters, and relationship resolution.
- FastMCP Apps dev UI launched successfully at a local port and returned HTTP 200; Playwright captured `catalog-app.png` and `catalog-app-full.png`.
- FastMCP Inspector launched successfully at a local port and returned HTTP 200. The inspector output included the MCP Apps sandbox endpoint.
- Note: FastMCP 4.0.10 Apps dev currently emits an internal `--no-reload` warning when invoked through the globally resolved CLI; using the project `.venv/bin/fastmcp` with the project directory on PATH starts the app successfully.
- Confirmed existing related work is separate EventCatalog/PDS project; no target files existed.

### Stage 1: packaging/CI + configurable registry root
- Issue #1 records the broader live-hub assessment and staged plan.
- Verified the initial GitHub Actions failure was setuptools automatic package discovery treating both `app` and `registry` as top-level packages.
- Fixed packaging by explicitly packaging `app` only; registry YAML remains external operational data.
- Added registry-root precedence: explicit `Registry(root)` → `REGISTRY_ROOT` → source-checkout `registry/` fallback.
- Added tests for default root, environment-configured root, explicit-over-environment precedence, and visible failure for a missing configured root.
- Updated README and architecture documentation for portable root selection.
- Stage 1 merged in PR #2; master run `36650481506` passed.

### Stage 2: catalog UX correctness
- Started from merged master `72bf342298c2a83293b2c42083309dbfd737ecad`.
- Added real nested Prefab kind and status filters.
- Added a hidden full-object search index covering stable IDs, names, descriptions, capabilities, outgoing/incoming relationships, metadata, and resolved host/location.
- Added resolved machine display names in the table/detail view.
- Added registry-level incoming/reverse relationship resolution and the `registry_incoming` FastMCP tool.
- Expanded details now show both outgoing and incoming relationships with display names and stable IDs.
- Added UI construction tests and a Playwright Chromium verifier against FastMCP's direct `/launch?tool=catalog` route.
- First CI attempt exposed a Prefab constraint: state keys must be identifier-safe and cannot contain hyphens. The state names were corrected to underscores.
- GitHub Actions run `36651211510` on commit `a68881456067f8d77cd90140ac1423a43afec494` passed:
  - 16 pytest tests
  - Python compilation
  - Chromium installation
  - FastMCP Apps preview startup
  - browser assertions for kind filter, status filter, stable-ID/full-object search, and policy rendering
- Browser receipt: `BROWSER_VERIFY succeeded: kind filter, status filter, full-object ID search, and policy view rendered; screenshot=/tmp/catalog-stage2.png`.
- The screenshot is ephemeral CI output and is not claimed as a durable artifact.


### Stage 3: source/interface model
- Started as a stacked branch from verified PR #3 head `9ba4dcfd6af1bd1d66f58177eddab025fa8e7825` because PR #3 remained open.
- Added optional `SourceSpec` with type, URI, authority, refresh mode, and writeback mode.
- Added optional `InterfaceSpec` with interface type, URI, adapter, status, and operations.
- Bounded source semantics to catalog/external/derived authority, manual/on-read/event/poll refresh, and none/controlled/direct writeback.
- Bounded interface status to declared/available/unavailable.
- Updated all 16 seed records with truthful `authority: catalog`, `refresh: manual`, and `writeback: controlled`.
- Added representative declared interfaces for Pi, Codex, filesystem, GitHub, browser, Mac control plane, Neo4j, Memgraph, and master-repo. These remain descriptive and are not claimed live.
- Source and interface fields now participate in both Python registry search and the Prefab hidden full-object search index.
- Prefab detail rows now expose source authority/refresh/writeback plus declared interfaces and operations.
- GitHub Actions run `36652704412` on commit `e97dcdce9c690141caeea960e6dd4cdb7c6f47b3` passed:
  - 20 pytest tests
  - Python compilation
  - Chromium installation
  - FastMCP Apps preview startup
  - browser search by stable ID, `cli://pi`, and `registry://agents/pi.yaml`
- Browser receipt: `BROWSER_VERIFY succeeded: kind/status filters, ID search, source search, declared-interface search, and policy view rendered; screenshot=/tmp/catalog-stage3.png`.
- Stage 4 is intentionally not started.


### Stage 4: workspace shell separation
- Issue #5 records the decision and acceptance criteria.
- Started from verified PR #4 head `970c4a7400ea95c347ba71f828730d57ab36dfad`; this branch is intentionally downstream of PR #4.
- Added `web/` as a separate Next.js workspace shell rather than modifying the FastMCP Apps development picker.
- Added Catalog, object inspector, Apps, Artifacts, Runs, and Review destinations.
- Catalog data is fetched from a read-only `/api/catalog` FastMCP custom route; the web shell does not read YAML directly and has no independent store.
- The Apps surface embeds the existing configurable Prefab/FastMCP Apps URL as a transitional development bridge.
- Artifacts, Runs, and Review deliberately show unbacked/empty states until authoritative models/providers exist.
- Added a GitHub Actions web-shell build job.
- Verification is not yet complete until the stacked PR head is read back green.


### Stage 5: FastMCP Generative UI
- Issue #9 records scope and acceptance.
- Confirmed current FastMCP API: `from fastmcp.apps.generative import GenerativeUI`; provider registers `generate_prefab_ui`, `search_prefab_components`, and the streaming renderer.
- Mounted `GenerativeUI()` without changing registry ownership or deterministic catalog behavior.
- Added server discovery test for all existing registry tools plus both Generative UI tools.
- Apps workspace now switches between Catalog app and Generative UI while preserving shell-owned navigation.
- Added Chromium workspace verification that clicks Apps → Generative UI and asserts the iframe targets `tool=generate_prefab_ui` and exposes both provider tool names in the surface description.
- PR #10 merged to `master`; native Generative UI remains mounted beside the deterministic catalog app.

### Stage 6: real skill discovery
- Reconciled against current `master` after PR #10 merged so native Generative UI is preserved.
- Added `SKILLS_ROOTS` configuration using the platform path separator.
- Added FastMCP `SkillsDirectoryProvider(reload=True)` when roots are configured.
- Added `CatalogView` so runtime projections overlay durable YAML records without moving provider logic into the registry domain layer.
- Stable runtime skill IDs use `skill.<directory-name>`.
- Matching YAML skills retain capabilities/relationships; runtime source/interface state is overlaid and the prior catalog source is retained in metadata.
- New discovered skills exist only in the runtime projection; no YAML is silently written.
- Added `skill_discovery_status` while keeping both Generative UI tools mounted.
- CI fixtures include one overlay skill and one runtime-only skill.
- Verification requires Python tests/compile, web build, Prefab browser discovery, actual FastMCP `skill://` resources, `/api/catalog` runtime projection, and the existing Generative UI workspace switcher.

### Stage 7: MCP federation
- Started from merged Stage 6 master `014df0c0e6ed05a7322ebf89f4d9b8edde17c90a`.
- Verified FastMCP 4.0.10 composition/proxy behavior from authoritative source: `create_proxy()` can bridge HTTP or local-file servers, `mount(..., namespace=...)` exposes upstream tools/resources/prompts under collision-safe namespaces, and proxies are lazy until an upstream request is made.
- Added `app/mcp_federation.py` for explicit catalog bindings, namespace validation, lazy proxy mounts, upstream discovery, 30-second cache, runtime status projection, and component metadata.
- Federation opt-in requires `type: mcp` plus `adapter: fastmcp-proxy`; the existing descriptive GitHub `mcp://github` record is intentionally not auto-connected.
- Supported target schemes are HTTP, HTTPS, and `file://` local Python MCP servers.
- Added explicit `namespace` to `InterfaceSpec` and included interface namespace + runtime metadata in catalog search.
- Added `mcp_federation_status(refresh=False)`; `refresh=true` forces a fresh upstream read-back.
- `/api/catalog?refresh_mcp=true` can also force a fresh federation probe.
- Added a real test MCP subprocess with one tool, resource, and prompt.
- Integration tests mount the fixture through FastMCP, verify namespaced components, execute the proxied tool, discover original upstream component names, project them onto the catalog object, and search by discovered component metadata.
- Functional branch run `36657399476` on commit `09ee164fd156a958227175a12cd2c5484d0b52b6` passed 30 pytest tests, Python compilation, the existing browser path, and the Next.js production build.
- Added a stronger browser/API fixture on `47f4615c6a5c8fe94fa8391374fceb35cc048eb4`: CI copies the real catalog to a temporary root, adds one live `file://` MCP binding, and verifies the runtime projection end to end without polluting durable seed data.

- End-to-end live federation run `36657579515` on commit `47f4615c6a5c8fe94fa8391374fceb35cc048eb4` passed:
  - 30 pytest tests
  - Python compilation
  - Next.js production build
  - temporary-registry FastMCP startup with one live `file://` proxy binding
  - Prefab search by discovered MCP component metadata
  - actual skill resource enumeration
  - `/api/catalog` skill + MCP federation projection verification
  - workspace `MCP: 1/1 available` plus Catalog/Generative UI verification
- Browser receipt: `BROWSER_VERIFY succeeded: skill discovery, live MCP federation metadata, stable IDs, and available interfaces rendered`.
- Catalog receipt: `CATALOG_HTTP_VERIFY succeeded: skill and MCP federation projections are present`.
- Workspace receipt: `WORKSPACE_VERIFY succeeded: live MCP federation status plus Catalog/Generative UI Apps rendered`.
