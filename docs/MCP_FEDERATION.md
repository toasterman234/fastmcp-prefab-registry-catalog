# MCP federation

Stage 7 lets an existing catalog object expose a real MCP server through FastMCP without introducing another service registry.

## Declare a binding

```yaml
id: resource.example
kind: resource
name: Example MCP
source:
  type: registry-yaml
  uri: registry://resources/example.yaml
  authority: catalog
  refresh: manual
  writeback: none
interfaces:
  - type: mcp
    uri: https://example.internal/mcp
    adapter: fastmcp-proxy
    namespace: example
    status: declared
```

The executable marker is `adapter: fastmcp-proxy`. An interface with `type: mcp` but another adapter remains descriptive.

Supported targets in Stage 7:
- `http://...`
- `https://...`
- `file:///absolute/path/to/server.py`

Do not put credentials in the URI.

## Runtime behavior

At server construction the catalog is scanned for explicit proxy bindings. Each binding is passed to FastMCP `create_proxy()` and mounted with its namespace.

FastMCP proxy construction is lazy: declaring and mounting a backend does not itself prove the backend is reachable. The catalog therefore performs a separate client read-back that lists:
- tools
- resources
- resource templates
- prompts
- negotiated protocol version

A successful mount and probe changes the runtime interface projection from `declared` to `available`. Failure produces `unavailable` plus error evidence in `metadata.federation`. Durable YAML is unchanged.

## Namespacing

Namespaces must be unique. A tool named `search` from namespace `github` is exposed by the parent as `github_search`; prompts are treated similarly. FastMCP transforms resource URIs under the namespace as well.

If `namespace` is omitted, the final segment of the catalog object ID is normalized and used. Explicit namespaces are recommended for durable interfaces.

## Runtime projection

Example runtime metadata:

```yaml
metadata:
  federation:
    example:
      status: available
      mounted: true
      protocol_version: 2026-07-28
      component_counts:
        tools: 4
        resources: 2
        resource_templates: 1
        prompts: 3
      components:
        tools: [search, fetch, create, update]
        resources: [example://schema, example://status]
        resource_templates: [example://objects/{id}]
        prompts: [review, summarize, plan]
```

Available component categories also add runtime capabilities such as `mcp-tools`, `mcp-resources`, and `mcp-prompts`.

## Refresh

Discovery uses a 30-second in-process cache and no background worker.

Force a fresh read-back through:

```text
mcp_federation_status(refresh=true)
GET /api/catalog?refresh_mcp=true
```

## Current boundary

Stage 7 does not implement:
- credential or secret storage
- OAuth configuration
- arbitrary command/package MCP config
- automatic network scanning
- background health polling
- mutation/writeback to the upstream server configuration

Those can be added later as explicit adapters without changing catalog identity.
