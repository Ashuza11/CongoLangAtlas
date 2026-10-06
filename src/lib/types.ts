export type ReviewCheck = "approved" | "unresolved" | "rejected";

export interface AtlasResource {
  id: string;
  title: string;
  type: string;
  modalities: string[];
  size: number | null;
  unit: string | null;
  format: string | null;
  access: string;
  licence: string | null;
  redistribution: string;
  geographic_scope: string;
  homepage_url: string;
  download_url: string | null;
  limitations: string | null;
  source: { citation: string; publisher: string; url: string };
}

export interface AtlasLanguage {
  id: string;
  name: string;
  iso: string;
  aliases: string[];
  region: string;
  classification_note: string | null;
  last_reviewed_at: string;
  review: {
    status: string;
    priority: string;
    blockers: string[];
    checks: Record<string, ReviewCheck>;
    ready_for_promotion: boolean;
  };
  resources: AtlasResource[];
  discovered_sources: DiscoveredSource[];
}

export interface DiscoveredSource {
  id: string;
  provider: string;
  kind: "catalogue" | "dataset" | "model" | "repository" | "research";
  title: string;
  url: string;
  review_status: "candidate";
  author?: string;
  authors?: string[];
  description?: string;
  licence?: string;
  access?: string;
  modalities?: string[];
  downloads?: number;
  stars?: number;
  publication_year?: number;
  publication_type?: string;
  venue?: string;
  open_access?: boolean;
  citations?: number;
  last_updated?: string;
}

export interface AtlasBundle {
  bundle_version: number;
  generated_at: string;
  source_commit: string;
  status: string;
  summary: {
    total: number;
    reviewed: number;
    high_priority: number;
    medium_priority: number;
    restricted_tracks: number;
    languages: number;
    resources: number;
    sources: number;
    open_download_tracks: number;
    discovered_sources: number;
  };
  languages: AtlasLanguage[];
}

export interface AtlasPlaceSelection {
  id: string;
  name: string;
  adminLevel: "province" | "territory";
  parentId?: string;
}
