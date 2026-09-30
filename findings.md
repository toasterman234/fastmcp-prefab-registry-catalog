# Findings: FastMCP Prefab Registry Catalog

## Existing related work
- The selected target directory did not exist before this task.
- The previously inspected `/Users/bencharney/my-catalog` is an existing Node/EventCatalog project with PDS projection files and no FastMCP/Prefab implementation. It is not being modified.

## API research
- Current global FastMCP CLI reports version `2.14.4`, while PyPI currently lists FastMCP `2.14.4` and `4.0.10`; the project will use a fresh isolated environment and pin the currently selected compatible release after installation.
- The global shell's `fastmcp` CLI is not importable from the system `python3`, so verification must use the project's isolated environment.
- `https://gofastmcp.com/mcp` returns an MCP endpoint with `Method not allowed` for plain HTTP GET, confirming it is an MCP endpoint rather than ordinary HTML documentation.
- The current web docs include Apps pages at `https://gofastmcp.com/apps/overview` and `https://gofastmcp.com/apps/prefab`.
- Current authoritative Apps docs show `@mcp.tool(app=True)` and Prefab `PrefabApp` returns. The page's current examples import components from `prefab_ui.components` and `PrefabApp` from `prefab_ui.app`.
- The current installed API is FastMCP `4.0.10`, `prefab-ui` `0.20.2`; `FastMCP.tool` accepts `app=True`, `FastMCP.resource` accepts URI templates, and Prefab supports `DataTable`, `DataTableColumn`, `ExpandableRow`, and `PrefabApp`.
- FastMCP Apps docs warn that Prefab is under active development and recommend pinning `prefab-ui`; this project pins both `fastmcp[apps]` and `prefab-ui`.
