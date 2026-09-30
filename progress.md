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
- GitHub Actions run 36650266857 passed installation, 11 tests, and Python compilation on commit `8e801ff3640936cd84067903dc298271ded6fb89`.
