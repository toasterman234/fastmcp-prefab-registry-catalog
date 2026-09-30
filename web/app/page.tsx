import { WorkspaceShell } from "../components/workspace-shell";
import type { RegistrySnapshot } from "../lib/types";

async function loadCatalog(): Promise<RegistrySnapshot> {
  const url = process.env.REGISTRY_API_URL ?? "http://127.0.0.1:9000/api/catalog";
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`catalog returned ${response.status}`);
    return await response.json();
  } catch (error) {
    return {
      objects: [],
      status_summary: "registry API unavailable",
      connected: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export default async function Home() {
  const snapshot = await loadCatalog();
  const appsUrl =
    process.env.NEXT_PUBLIC_MCP_APPS_URL ?? "http://127.0.0.1:9090/launch?tool=catalog";
  return <WorkspaceShell snapshot={snapshot} appsUrl={appsUrl} />;
}
