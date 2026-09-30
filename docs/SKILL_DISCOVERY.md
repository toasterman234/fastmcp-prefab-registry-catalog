# Real skill discovery

Stage 5 connects FastMCP's directory-backed skills provider to the catalog.

## Configuration

Set `SKILLS_ROOTS` to one or more directories, separated by the platform path separator:

```bash
export SKILLS_ROOTS="/path/to/skills:/another/path/to/skills"
```

Each configured root is scanned for immediate child directories containing `SKILL.md`.

With FastMCP 4.0.10, `SkillsDirectoryProvider` uses first-root-wins semantics for duplicate skill directory names. The server uses `reload=True` for the FastMCP provider, so resource requests re-scan the configured roots.

## Runtime behavior

For a discovered directory:

```text
my-skill/
├── SKILL.md
└── reference.md
```

FastMCP exposes:

```text
skill://my-skill/SKILL.md
skill://my-skill/_manifest
skill://my-skill/{path*}
```

The first two are listable resources. Supporting files use the resource template.

The catalog projects the same discovered skill as:

```yaml
id: skill.my-skill
kind: skill
source:
  type: skill-directory
  authority: external
  refresh: on-read
  writeback: none
interfaces:
  - type: mcp-resource
    uri: skill://my-skill/SKILL.md
    adapter: fastmcp-skills
    status: available
```

## Stable identity and overlays

The stable catalog ID is `skill.<directory-name>`.

If that ID already exists in YAML:
- capabilities and relationships remain catalog annotations;
- the runtime skill description can refresh from SKILL.md;
- the source becomes the discovered skill directory;
- the available MCP resource interface is merged with existing interfaces;
- the previous catalog source is retained in metadata as `catalog_source`.

If a discovered skill has no YAML record, it is added only to the runtime catalog projection. No YAML file is silently created.

## Truthfulness boundary

`status: available` means FastMCP successfully discovered the directory and exposed the skill through the configured provider in this process.

It does **not** mean:
- the skill has been installed on other machines;
- the skill can mutate its source;
- the standardized MCP Skills extension is enabled.

FastMCP 4.0.10 exposes these skills through ordinary MCP resources. The separate standardized Skills extension work is not treated as available here.

## No writeback

Stage 5 is read-only. It does not install, edit, delete, copy, or synchronize skills.
