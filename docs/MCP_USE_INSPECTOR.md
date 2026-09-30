# mcp-use Inspector integration plan

## Status

Planning only. No runtime or dependency changes are implemented on this branch yet.

## Why this fits the current architecture

The repository already separates responsibilities:

```text
configured YAML registry
  -> Python domain/catalog layer
  -> FastMCP tools/resources/apps/providers
  -> Prefab app surfaces + separate workspace shell
```

Recent work also added catalog-declared MCP federation. That means the project now has enough MCP-native capability that a generic MCP host can become the thin interactive dashboard instead of continuing to grow a bespoke shell for generic MCP concerns.

The proposed role for **mcp-use Inspector** is therefore:

- generic MCP host/dashboard
- server connection management
- tool/resource/prompt discovery
- generic tool invocation/forms
- MCP App/widget rendering
- saved/repeatable calls where supported
- optional chat against connected MCP capabilities
- connection/runtime status

It is **not** a new source of truth and must not own catalog data, source authority, registry semantics, or provider/federation policy.

## Existing capabilities that should map directly

The current FastMCP server already exposes the capabilities mcp-use should consume:

- registry tools and resources
- deterministic Prefab catalog app
- Generative UI tools/apps
- real skill resources from `SkillsDirectoryProvider`
- federated upstream MCP tools/resources/prompts
- runtime federation status/projection
- HTTP/catalog projection used by the existing workspace shell

The integration should prove which of these are visible and usable in mcp-use without adapting the domain model.

## Target architecture

```text
                         mcp-use Inspector
                    thin MCP host/dashboard
                              |
                 tools / resources / prompts / apps
                              |
                              v
                    FastMCP server (existing)
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
   YAML/domain catalog   Prefab/GenUI apps   MCP federation
                                                  |
                                      catalog-declared upstream MCPs
```

The existing Next.js shell remains available during evaluation. This stage should decide whether mcp-use can replace part or all of its generic MCP-host responsibilities. Do not delete the shell during the initial integration.

## Scope

### Phase 1 — compatibility spike

Run the existing FastMCP server and connect mcp-use Inspector to it.

Verify and record:

1. server connection succeeds using the project's normal local transport
2. existing registry tools are discoverable
3. registry resources are readable
4. prompts, if present, are discoverable
5. deterministic Prefab catalog app renders
6. Generative UI app/tool surfaces are usable
7. app-originated tool calls work where supported
8. federated upstream tools/resources/prompts are visible through the FastMCP server
9. runtime errors and unavailable upstreams are represented truthfully
10. reconnect/restart behavior is acceptable for local use

No code changes should be made to force success until the compatibility result is documented.

### Phase 2 — local developer/runtime entrypoint

If Phase 1 passes, add the smallest reproducible integration surface possible.

Preferred order:

1. document an external `npx`/package invocation if sufficient
2. otherwise add a repo-local script or task wrapper
3. only add package/dependency coupling if required

The FastMCP server remains independently runnable. mcp-use must remain a replaceable client/host.

### Phase 3 — dashboard fit assessment

Compare mcp-use with the current `web/` shell for generic responsibilities:

- connection/server picker
- tool browser
- resource browser
- prompt browser
- app host
- invocation forms
- invocation history/saved calls
- runtime/connection status
- chat

Classify each responsibility as:

- **delegate to mcp-use**
- **keep in repo shell**
- **specialized app surface**
- **not needed**

The likely desired end-state is to keep only project-specific surfaces in this repo and delegate generic MCP hosting to mcp-use.

### Phase 4 — optional shell simplification

Only after explicit promotion from the compatibility/evaluation stages:

- remove duplicated generic MCP-host UI from `web/`
- keep project-specific navigation or views only where they add value
- preserve Prefab/GenUI apps as MCP-native surfaces
- preserve YAML/domain/FastMCP authority boundaries
- update architecture documentation and CI accordingly

This phase is intentionally not approved by creation of this planning branch.

## Non-goals

Do not:

- replace YAML as durable catalog authority
- move catalog/domain logic into mcp-use
- duplicate MCP federation inside the dashboard
- add a second registry/database
- make mcp-use a required runtime dependency before compatibility is proven
- remove the existing workspace shell during the spike
- change provider authority/writeback semantics
- treat a rendered screen as proof that tool/resource behavior works
- claim production readiness, auth, persistence, or mobile support without verification

## Verification matrix

| Capability | Existing source | Verification required in mcp-use |
|---|---|---|
| Registry tools | FastMCP | discover + invoke + inspect result |
| Registry resources | FastMCP | list/read |
| Prefab catalog | MCP App | render + interact |
| Generative UI | FastMCP provider | discover + invoke/render |
| Skills | SkillsDirectoryProvider | resource discovery/read |
| MCP federation | fastmcp-proxy | discover upstream components + invoke one real proxied tool |
| Unavailable upstream | runtime projection | visible failure/status; no false available state |
| Restart/reconnect | FastMCP + host | server restart followed by successful rediscovery |

## Acceptance criteria for an implementation PR

- [ ] mcp-use Inspector can connect to the repo's FastMCP server using documented commands
- [ ] existing local FastMCP/Prefab flows still work independently
- [ ] registry tools and resources are visible and usable
- [ ] deterministic Prefab catalog app renders in the host, or the incompatibility is documented with evidence
- [ ] Generative UI behavior is verified or explicitly documented as unsupported
- [ ] one real federated MCP tool call is executed through the existing federation layer
- [ ] an unavailable/broken upstream does not appear falsely healthy
- [ ] no second source of truth or duplicated federation configuration is introduced
- [ ] tests remain green
- [ ] browser/integration evidence is recorded
- [ ] branch/PR CI is read back green before completion is claimed

## Decision gate

After Phase 1, record one of three outcomes:

1. **Adopt as primary thin dashboard** — enough capability exists to delegate generic MCP hosting.
2. **Keep as developer/operator console** — useful for inspection but insufficient as the primary workspace.
3. **Reject** — material incompatibility or duplication outweighs benefit.

Do not proceed to shell removal or architectural replacement until one of these outcomes is explicitly recorded.

## Relationship to existing work

- Issue #1 remains the broad evolution roadmap.
- Issue #5 established the shell/app separation this integration builds on.
- Issue #9 established Generative UI as an app surface rather than the global shell.
- PR #12 / Stage 7 established MCP federation, which should be consumed through the existing FastMCP server rather than reimplemented in the dashboard.

## Recommended next action

Run the bounded Phase 1 compatibility spike against the current `master` behavior, record evidence, then decide whether mcp-use should become the primary dashboard or remain a development console.
