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
