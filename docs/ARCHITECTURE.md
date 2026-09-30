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

`app/models.py` defines the small generic Pydantic schema. `app/registry.py` resolves the registry root, loads YAML, and owns list, get, search, filter, outgoing/incoming relationship resolution, and validation. It does not import FastMCP or Prefab and can be used from ordinary Python code.

### Source and interface metadata

Stage 3 adds two optional generic concepts without changing runtime ownership:

```yaml
source:
  type: registry-yaml
  uri: registry://agents/pi.yaml
  authority: catalog
  refresh: manual
  writeback: controlled

interfaces:
  - type: cli
    uri: cli://pi
    adapter: pi
    status: declared
    operations: [inspect, invoke]
```

`source` answers where the record's current truth comes from and how that truth may be refreshed or changed:

- `authority: catalog` — the registry record is authoritative today.
- `authority: external` — an external system is authoritative; the catalog should project it.
- `authority: derived` — the record is generated from another source.
- `refresh`: `manual`, `on-read`, `event`, or `poll`.
- `writeback`: `none`, `controlled`, or `direct`.

`interfaces[]` describes ways the underlying thing may be reached. Interface `status: declared` is descriptive only and does **not** mean the adapter has been connected or verified. Future live-adapter stages may promote an interface to `available` only after runtime verification.

The source/interface model is intentionally generic. It does not implement synchronization, polling, MCP proxying, agent invocation, database connectivity, or file mutation.

### FastMCP

`app/server.py` is an interface layer only. It exposes registry operations as MCP tools, publishes individual objects and the full snapshot as readable resources, and adds the `catalog` app tool. FastMCP is not the database and does not own catalog state.

### Prefab

`app/ui.py` builds a compact table-oriented UI returned by the `catalog` tool. Prefab is used only for presentation. The UI receives registry data and does not load YAML or implement domain rules. The catalog exposes source authority and declared interfaces but does not imply those interfaces are live.

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

A future live integration can use the source/interface metadata to bind a record to a provider or adapter without changing the catalog's identity model:

```text
RegistryObject
  ├─ source      → where truth lives
  ├─ interfaces  → declared ways to reach it
  └─ relationships → semantic links
             ↓
       future provider/adapter
             ↓
       authoritative system
```

## Packaging boundary

The Python distribution packages `app` only. Registry YAML is operational/domain data and is not implicitly bundled into the wheel. Portable deployments should set `REGISTRY_ROOT` to the authoritative catalog location.

## Deliberate current constraints

- No persistence provider beyond YAML
- No CRUD or editing surface
- No live source refresh
- No synchronization or writeback execution
- No authentication
- No background refresh or workers
- No graph database or graph visualization
- No agent invocation or policy execution
- No broad platform abstractions

The model accepts unknown extra fields to make new kinds possible without changing application architecture, while required common fields and source/interface semantics remain validated by Pydantic.


## Workspace shell

Stage 4 separates global workspace UX from Prefab app UX.

```text
Configured YAML registry
      ↓
Python registry domain layer
      ↓
FastMCP
 ├─ MCP tools/resources
 ├─ read-only /api/catalog projection
 └─ Prefab / MCP App surfaces
      ↓
web/ workspace shell
 ├─ Catalog / Bases-style projection
 ├─ Inspector
 ├─ Apps host surface
 ├─ Artifacts
 ├─ Runs
 └─ Review
```

Responsibility boundary:
- the shell owns navigation, density, workspace layout, and saved human-facing surfaces
- FastMCP owns capabilities, tools/resources/providers, and the control/data interface
- Prefab owns deterministic interactive app surfaces
- generated UI belongs in the Apps surface rather than becoming the global shell
- YAML remains authoritative; the shell never reads or writes registry YAML directly

The current Apps embedding URL is a development bridge to `fastmcp dev apps`, not a claim of a production MCP Apps host. Artifacts, Runs, and Review are visible shell destinations but remain intentionally unbacked until authoritative models/providers exist.
