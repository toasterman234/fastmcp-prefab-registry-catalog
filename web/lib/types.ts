export type RegistryObject = {
  id: string;
  kind: string;
  name: string;
  description?: string;
  status: string;
  capabilities?: string[];
  source?: {
    type?: string;
    uri?: string;
    authority?: string;
    refresh?: string;
    writeback?: string;
  } | null;
  interfaces?: Array<{
    type?: string;
    uri?: string | null;
    adapter?: string | null;
    namespace?: string | null;
    status?: string;
    operations?: string[];
  }>;
  relationships?: Record<string, string[]>;
  metadata?: Record<string, unknown>;
};

export type RegistrySnapshot = {
  objects: RegistryObject[];
  status_summary: string;
  connected?: boolean;
  error?: string;
  discovery?: {
    skills?: {
      enabled?: boolean;
      provider?: string | null;
      roots?: string[];
      missing_roots?: string[];
      discovered_count?: number;
      discovered_ids?: string[];
      refresh?: string | null;
      protocol_surface?: string | null;
    };
    mcp_federation?: {
      enabled?: boolean;
      provider?: string | null;
      configured_count?: number;
      available_count?: number;
      unavailable_count?: number;
      cache_ttl_seconds?: number;
      refreshed_at?: string | null;
      servers?: Array<Record<string, unknown>>;
    };
  };
};
