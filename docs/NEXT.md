# Next extensions

The repository now has a YAML-backed durable catalog, source/interface semantics, a separate workspace shell, deterministic Prefab apps, native FastMCP Generative UI, real directory-backed skill discovery, and catalog-declared MCP federation.

## Completed foundations

- configurable external registry root
- kind/status filtering and full-object search
- outgoing/incoming relationship views
- source authority / refresh / writeback metadata
- declared-versus-runtime-available interfaces
- separate workspace shell and read-only `/api/catalog` projection
- native FastMCP Generative UI inside Apps
- real `SKILL.md` discovery through `SkillsDirectoryProvider`
- runtime skill projection with stable IDs
- catalog-declared MCP proxy mounts with namespaces
- upstream MCP tools/resources/prompts discovery and runtime projection
- explicit federation refresh/read-back
- browser, proxy-tool-call, HTTP-resource, API-projection, and web-build verification

## Next: files/docs/policies discovery

The next narrow increment should make arbitrary filesystem-backed Markdown/YAML documents discoverable through the same catalog/source model.

Requirements:
- do not create a parallel document database
- preserve explicit authority and writeback rules
- attach discovered files to existing catalog identities when possible
- distinguish authored documents from generated projections
- keep filesystem/provider scope explicit rather than recursively scanning the whole machine
- provide read-back evidence before marking file interfaces available

## Later independent stages

- controlled editing/CRUD and writeback
- authenticated MCP target bindings / secret references
- package/command MCP target configs if needed
- live machine/service health
- agent invocation adapters
- database schema/query adapters
- policy evaluation
- JEv search/routing
- graph/relationship visualization
- optional SQLite only if YAML becomes limiting

Each later increment should remain independently scoped and verified.
