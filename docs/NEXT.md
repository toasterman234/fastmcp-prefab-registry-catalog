# Next extensions

The registry now has a read-only YAML catalog, FastMCP exposure, a Prefab viewer, real catalog filters/search, reverse relationships, and optional source/interface metadata.

## Completed foundations

- configurable external registry root
- real kind/status filtering
- full-object catalog search
- outgoing and incoming relationship views
- source authority / refresh / writeback metadata
- declared interface metadata
- browser verification in CI

## Next: stage 4 — real skill discovery

The next narrow increment should replace descriptive skill records with discovery from real skill directories where available.

Candidate shape:

```text
SKILL.md directories
      ↓
FastMCP SkillsDirectoryProvider
      ↓
discovered skills/resources
      ↓
catalog projection
```

Requirements before marking any discovered source/interface as live:

- retain stable catalog IDs
- preserve explicit source authority
- do not silently overwrite catalog-controlled fields
- distinguish discovered/available from merely declared
- provide refresh/read-back evidence
- keep the provider optional and replaceable

## Later independent stages

- MCP server discovery/federation
- arbitrary filesystem/docs/policies discovery
- editing/CRUD
- controlled refresh/writeback
- SQLite or another persistence provider if YAML becomes limiting
- live machine status
- agent invocation
- policy evaluation
- JEv search/routing
- graph/relationship visualization

These are not prerequisites for the current registry and should not be added as hidden infrastructure. Each requires an explicit architecture decision and verification plan before implementation.
