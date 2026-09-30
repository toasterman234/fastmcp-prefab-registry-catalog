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
};
