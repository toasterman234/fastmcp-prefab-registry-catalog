# Architecture

## Responsibilities

### YAML registry

`registry/` is the durable v0 source of truth in a source checkout. Files are organized by object kind for readability. YAML is plain, portable, reviewable, and easy to replace with real inventory records later.

The registry source is intentionally external to the Python package. Runtime root selection is:

1. explicit `Registry(root)`
2. `REGISTRY_ROOT`
3. the repository `registry/` development fallback

A configured but missing root is a validation error; the application does not silently switch authorities.

### Python registry library

`app/models.py` defines the small generic Pydantic schema. `app/registry.py` resolves the registry root, loads YAML, and owns list, get, search, filter, relationship resolution, and validation operations. It does not import FastMCP or Prefab and can be used from ordinary Python code.

### FastMCP

`app/server.py` is an interface layer only. It exposes registry operations as MCP tools, publishes individual objects and the full snapshot as readable resources, and adds the `catalog` app tool. FastMCP is not the database and does not own catalog state.

### Prefab

`app/ui.py` builds a compact table-oriented UI returned by the `catalog` tool. Prefab is used only for presentation. The UI receives registry data and does not load YAML or implement domain rules. Table search and expandable rows keep the catalog readable without creating a second domain model.

## Data flow

```text
Configured YAML registry root
      ↓
Python registry library
      ↓
FastMCP
 ├─ Resources
 ├─ Tools
 └─ Prefab App
      ↓
Catalog UI
```

## Packaging boundary

The Python distribution packages `app` only. Registry YAML is operational/domain data and is not implicitly bundled into the wheel. Portable deployments should set `REGISTRY_ROOT` to the authoritative catalog location.

## Deliberate v0 constraints

- No persistence provider beyond YAML
- No CRUD or editing surface
- No authentication
- No background refresh or workers
- No graph database or graph visualization
- No agent invocation or policy execution
- No broad platform abstractions

The model accepts unknown extra fields to make new kinds possible without changing application architecture, while required common fields remain validated by Pydantic.
