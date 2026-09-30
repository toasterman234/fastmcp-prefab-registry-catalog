# Workspace shell

This directory is the human workspace shell. It is intentionally separate from Prefab and from the FastMCP development Apps picker.

## Responsibilities

The shell owns:
- navigation and workspace layout
- Bases-style catalog projection
- object inspector
- Apps, Artifacts, Runs, and Review surfaces

FastMCP owns:
- MCP tools/resources/providers
- control and composition
- the read-only registry projection used by this shell

Prefab owns:
- deterministic interactive app surfaces
- forms, approvals, dashboards, and other MCP App UI

The shell does **not** load YAML directly and is not a second source of truth.

## Run

Start FastMCP over HTTP:

```bash
fastmcp run app/server.py --transport http --port 9000
```

Start the existing Prefab Apps development host when you want the embedded app surface:

```bash
fastmcp dev apps app/server.py --mcp-port 9000 --dev-port 9090 --no-reload
```

Then:

```bash
cd web
npm install
npm run dev
```

Environment variables:

- `REGISTRY_API_URL` defaults to `http://127.0.0.1:9000/api/catalog`
- `NEXT_PUBLIC_MCP_APPS_URL` defaults to `http://127.0.0.1:9090/launch?tool=catalog`

The iframe path is a transitional development host. A production MCP Apps host is intentionally not claimed or implemented in this stage.


## App surfaces

The Apps section has two explicit modes:
- **Catalog app** — deterministic Prefab UI returned by `catalog()`
- **Generative UI** — FastMCP's native `GenerativeUI` provider, launched through `generate_prefab_ui`

The development iframe still uses `fastmcp dev apps`. This remains a development bridge, not a production MCP Apps host.
