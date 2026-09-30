"use client";

import { useMemo, useState } from "react";
import type { RegistryObject, RegistrySnapshot } from "../lib/types";

type Surface = "catalog" | "apps" | "artifacts" | "runs" | "review";

const nav: Array<{ id: Surface; label: string; hint: string }> = [
  { id: "catalog", label: "Catalog", hint: "registry" },
  { id: "apps", label: "Apps", hint: "Prefab / MCP" },
  { id: "artifacts", label: "Artifacts", hint: "outputs" },
  { id: "runs", label: "Runs", hint: "execution" },
  { id: "review", label: "Review", hint: "governance" },
];

function Catalog({ snapshot }: { snapshot: RegistrySnapshot }) {
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState("all");
  const [selected, setSelected] = useState<RegistryObject | null>(null);
  const skillDiscovery = snapshot.discovery?.skills;
  const mcpFederation = snapshot.discovery?.mcp_federation;

  const kinds = useMemo(
    () => [...new Set(snapshot.objects.map((item) => item.kind))].sort(),
    [snapshot.objects],
  );

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return snapshot.objects.filter((item) => {
      const matchesKind = kind === "all" || item.kind === kind;
      const blob = [
        item.id,
        item.kind,
        item.name,
        item.description ?? "",
        item.status,
        ...(item.capabilities ?? []),
        item.source?.type ?? "",
        item.source?.authority ?? "",
        ...(item.interfaces ?? []).flatMap((entry) => [
          entry.type ?? "",
          entry.uri ?? "",
          entry.adapter ?? "",
          entry.namespace ?? "",
          entry.status ?? "",
          ...(entry.operations ?? []),
        ]),
        JSON.stringify(item.metadata ?? {}),
      ]
        .join(" ")
        .toLowerCase();
      return matchesKind && (!q || blob.includes(q));
    });
  }, [snapshot.objects, query, kind]);

  return (
    <div className="catalog-layout">
      <section className="surface">
        <div className="surface-header">
          <div>
            <h1>Catalog</h1>
            <p>
              {snapshot.objects.length} objects · {snapshot.status_summary}
              {skillDiscovery?.enabled ? ` · skills: ${skillDiscovery.discovered_count ?? 0} discovered` : ""}
              {mcpFederation?.enabled ? ` · MCP: ${mcpFederation.available_count ?? 0}/${mcpFederation.configured_count ?? 0} available` : ""}
            </p>
          </div>
          <span className={snapshot.connected === false ? "status warning" : "status ok"}>
            {snapshot.connected === false ? "API offline" : "live projection"}
          </span>
        </div>

        <div className="toolbar">
          <input
            aria-label="Search catalog"
            placeholder="Search catalog…"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <select value={kind} onChange={(event) => setKind(event.target.value)}>
            <option value="all">All types</option>
            {kinds.map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </div>

        {snapshot.connected === false && (
          <div className="notice">
            The workspace shell is running, but the FastMCP registry HTTP projection is unavailable.
            Start FastMCP over HTTP on port 9000 or set <code>REGISTRY_API_URL</code>.
          </div>
        )}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th><th>Type</th><th>Status</th><th>Source</th><th>Authority</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((item) => (
                <tr key={item.id} onClick={() => setSelected(item)} className={selected?.id === item.id ? "selected" : ""}>
                  <td><strong>{item.name}</strong><small>{item.id}</small></td>
                  <td>{item.kind}</td>
                  <td><span className="pill">{item.status}</span></td>
                  <td>{item.source?.type ?? "—"}</td>
                  <td>{item.source?.authority ?? "—"}</td>
                </tr>
              ))}
              {!rows.length && (
                <tr><td colSpan={5} className="empty-cell">No catalog rows match this view.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <aside className="inspector">
        {selected ? (
          <>
            <span className="eyebrow">{selected.kind}</span>
            <h2>{selected.name}</h2>
            <code>{selected.id}</code>
            <p>{selected.description || "No description."}</p>
            <dl>
              <dt>Status</dt><dd>{selected.status}</dd>
              <dt>Capabilities</dt><dd>{selected.capabilities?.join(", ") || "None"}</dd>
              <dt>Source</dt><dd>{selected.source?.uri || selected.source?.type || "None"}</dd>
              <dt>Authority</dt><dd>{selected.source?.authority || "None"}</dd>
              <dt>Writeback</dt><dd>{selected.source?.writeback || "None"}</dd>
              <dt>Interfaces</dt>
              <dd>
                {selected.interfaces?.length
                  ? selected.interfaces.map((item) => `${item.type ?? "interface"}:${item.status ?? "unknown"}`).join(", ")
                  : "None"}
              </dd>
            </dl>
          </>
        ) : (
          <div className="empty-state"><strong>Select a row</strong><p>Object details stay out of the table until you need them.</p></div>
        )}
      </aside>
    </div>
  );
}

function Apps({ appsUrl }: { appsUrl: string }) {
  const [appSurface, setAppSurface] = useState<"catalog" | "generative">("catalog");
  const appBase = appsUrl.includes("/launch?") ? appsUrl.split("/launch?")[0] : appsUrl.replace(/\/$/, "");
  const currentUrl =
    appSurface === "catalog"
      ? `${appBase}/launch?tool=catalog`
      : `${appBase}/launch?tool=generate_prefab_ui`;

  return (
    <section className="surface full-height">
      <div className="surface-header">
        <div>
          <h1>Apps</h1>
          <p>Deterministic Prefab apps and open-ended FastMCP Generative UI live here.</p>
        </div>
        <a className="button" href={currentUrl} target="_blank" rel="noreferrer">Open separately</a>
      </div>

      <div className="app-tabs" role="tablist" aria-label="App surfaces">
        <button
          data-testid="app-surface-catalog"
          className={appSurface === "catalog" ? "app-tab active" : "app-tab"}
          onClick={() => setAppSurface("catalog")}
          role="tab"
          aria-selected={appSurface === "catalog"}
        >
          Catalog app
        </button>
        <button
          data-testid="app-surface-generative"
          className={appSurface === "generative" ? "app-tab active" : "app-tab"}
          onClick={() => setAppSurface("generative")}
          role="tab"
          aria-selected={appSurface === "generative"}
        >
          Generative UI
        </button>
      </div>

      <div className="app-context">
        {appSurface === "catalog"
          ? "Known-shape registry browsing. This remains the deterministic Prefab surface."
          : "FastMCP GenerativeUI provider. An agent can compose Prefab UI at runtime using generate_prefab_ui and search_prefab_components."}
      </div>

      <div className="app-frame-wrap">
        <iframe
          key={currentUrl}
          title={appSurface === "catalog" ? "Catalog Prefab app" : "FastMCP Generative UI"}
          src={currentUrl}
          className="app-frame"
        />
      </div>
    </section>
  );
}

function ReservedSurface({ title, copy }: { title: string; copy: string }) {
  return (
    <section className="surface">
      <div className="surface-header"><div><h1>{title}</h1><p>{copy}</p></div><span className="status neutral">reserved</span></div>
      <div className="empty-state large">
        <strong>No fake backing model</strong>
        <p>This surface is part of the shell now, but it will remain empty until the repository has an authoritative model/provider for it.</p>
      </div>
    </section>
  );
}

export function WorkspaceShell({ snapshot, appsUrl }: { snapshot: RegistrySnapshot; appsUrl: string }) {
  const [surface, setSurface] = useState<Surface>("catalog");

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">F</span><div><strong>FastMCP</strong><small>workspace</small></div></div>
        <nav>
          {nav.map((item) => (
            <button
              key={item.id}
              data-testid={`nav-${item.id}`}
              onClick={() => setSurface(item.id)}
              className={surface === item.id ? "active" : ""}
            >
              <span>{item.label}</span><small>{item.hint}</small>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span>Shell owns navigation.</span>
          <span>FastMCP owns capabilities.</span>
          <span>Prefab owns app surfaces.</span>
        </div>
      </aside>

      <div className="main-pane">
        <header className="topbar">
          <div><strong>Environment Workspace</strong><span>/ {nav.find((item) => item.id === surface)?.label}</span></div>
          <span className="topbar-note">read-only shell increment</span>
        </header>
        <div className="content">
          {surface === "catalog" && <Catalog snapshot={snapshot} />}
          {surface === "apps" && <Apps appsUrl={appsUrl} />}
          {surface === "artifacts" && <ReservedSurface title="Artifacts" copy="Durable generated outputs, previews, reports, files, and app-produced artifacts." />}
          {surface === "runs" && <ReservedSurface title="Runs" copy="Execution history and evidence will project here when a run model is authoritative." />}
          {surface === "review" && <ReservedSurface title="Review" copy="Approvals, proposed changes, verification, and governance queues belong here." />}
        </div>
      </div>
    </main>
  );
}
