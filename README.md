# FastMCP Prefab Registry Catalog

A deliberately small, portable catalog for describing an agent environment.

The v0 source of truth is a set of YAML files. Pydantic validates records, the ordinary Python registry library provides domain operations, FastMCP exposes tools and resources, and Prefab renders the catalog UI.

## Repository handoff

Start with [`AGENTS.md`](AGENTS.md) for the layout, invariants, commands, verification baseline, and safe change procedure. [`docs/REPOSITORY.md`](docs/REPOSITORY.md) records what was implemented and the last verified state.

## Architecture

```text
registry/*.yaml
      ↓
app/models.py + app/registry.py
      ↓
app/server.py (FastMCP)
 ├─ MCP resources
 ├─ MCP tools
 └─ Prefab App tool
      ↓
Environment Catalog UI
```

This project is intentionally local and narrow. It has no database, authentication, React/Next.js frontend, workers, agent runtime, or workflow engine.

## Catalog UI

The Prefab catalog currently supports:

- kind filters
- status filters
- sorting and pagination
- search across names, stable IDs, descriptions, capabilities, relationships, metadata, and host/location
- resolved machine display names
- expandable object details
- resolved outgoing relationships
- reverse/incoming relationships

The browser path is verified in CI using Chromium against a real `fastmcp dev apps` preview rather than only testing Python component construction.

## Install and run

Create or refresh the isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

Run the FastMCP development app:

```bash
env PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp dev apps app/server.py
```

Run the MCP Inspector:

```bash
env PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp dev inspector app/server.py
```

The `app/server.py` module is importable as a normal Python module for tests and registry use.

## Registry root configuration

The YAML registry remains external durable data rather than Python package data.

Registry-root precedence is:

1. an explicit root passed to `Registry(root)`
2. the `REGISTRY_ROOT` environment variable
3. the repository's `registry/` directory as the source-checkout development fallback

For a portable installation, point the service at the authoritative catalog explicitly:

```bash
export REGISTRY_ROOT=/path/to/environment-registry
fastmcp run app/server.py
```

If a configured registry root does not exist, registry validation reports an error rather than silently falling back to another source.

## Schema

Every object uses the common fields:

```yaml
id: agent.pi.mac
kind: agent
name: Pi
description: Pi agent running on the Mac
status: active
location:
  machine: machine.mac-mini
capabilities:
  - filesystem
relationships:
  runs_on:
    - machine.mac-mini
metadata:
  seed: true
  example: true
```

`location` is optional. `capabilities`, `relationships`, and `metadata` default to empty values. The Pydantic model allows additional fields so a new kind can add narrow metadata without changing the registry architecture.

## Adding an object

1. Add a YAML file below the matching `registry/<kind>/` directory, or below the configured `REGISTRY_ROOT`.
2. Use a globally unique `id`.
3. Set `metadata.seed: true` and `metadata.example: true` for replaceable examples.
4. Use relationship target IDs, not display names.
5. Run validation and tests:

```bash
.venv/bin/python -c 'from app.registry import validate_registry; print(validate_registry().model_dump_json(indent=2))'
.venv/bin/python -m pytest -q
```

## Adding a new object kind

Create a new directory such as `registry/integrations/` and add YAML records with `kind: integration`. No Python schema or dispatch change is required. The generic model, loader, filters, search, FastMCP tools, resources, and Prefab table discover kinds from loaded records.

## Seed data

The seed set includes Pi, Codex, Mac Mini, Zima, OVH, two skills, two policies, three resources, Neo4j, Memgraph, master-repo, and a root-cause-analysis playbook. These are clearly marked as `seed` and `example` metadata and are intended to be replaced by actual inventory later.

## Tests

The test suite covers YAML loading, Pydantic defaults and validation, search, filters, outgoing/incoming relationship resolution, missing relationship references, duplicate IDs, registry-root configuration, and catalog UI construction. GitHub Actions additionally runs a real Chromium smoke verification for the rendered Prefab app.
