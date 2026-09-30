# Next extensions

The repository now has a YAML-backed durable catalog, source/interface semantics, a separate workspace shell, deterministic Prefab apps, native FastMCP Generative UI, and configurable real directory-backed skill discovery.

## Completed foundations

- configurable external registry root
- kind/status filtering and full-object search
- outgoing/incoming relationship views
- source authority / refresh / writeback metadata
- declared-versus-available interfaces
- separate workspace shell and read-only `/api/catalog` projection
- native FastMCP Generative UI inside Apps
- real `SKILL.md` discovery through `SkillsDirectoryProvider`
- runtime skill projection with stable IDs
- browser, HTTP-resource, API-projection, and web-build verification

## Next: MCP federation

The next narrow increment should register/proxy real MCP servers and attach their tools/resources/prompts to catalog entities.

Requirements:
- preserve the current catalog identity model
- use source/interface metadata rather than inventing a second registry
- distinguish configured endpoints from runtime-reachable endpoints
- namespace or otherwise prevent component collisions
- expose connection/read-back evidence
- keep backend servers independently replaceable

## Later independent stages

- arbitrary filesystem/docs/policies discovery
- editing/CRUD
- controlled refresh/writeback
- optional SQLite or other persistence only if YAML becomes limiting
- live machine status
- agent invocation
- policy evaluation
- JEv search/routing
- graph/relationship visualization

Each later increment should remain independently scoped and verified.
