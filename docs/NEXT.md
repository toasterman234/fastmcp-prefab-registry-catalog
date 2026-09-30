# Next extensions (intentionally not implemented)

The current read-only v0 deliberately stops at YAML-backed catalog data, FastMCP exposure, and the Prefab viewer.

The v0 catalog is read-only and YAML-backed. Possible later extensions, in deliberately separate increments:

- editing/CRUD
- SQLite provider
- filesystem auto-discovery
- MCP server discovery
- live machine status
- agent invocation
- policy evaluation
- JEv search/routing
- graph/relationship visualization

These are not prerequisites for the current registry and should not be added as hidden infrastructure. Each would need an explicit architecture decision and verification plan before implementation.
