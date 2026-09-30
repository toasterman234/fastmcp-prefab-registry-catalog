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

1. Add a YAML file below the matching `registry/<kind>/` directory.
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

The test suite covers YAML loading, Pydantic defaults and validation, search, filters, relationship resolution, missing relationship references, and duplicate IDs.
