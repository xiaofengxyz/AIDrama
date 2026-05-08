export const WORKBENCH_STEP_IDS = [
  "script",
  "art_direction",
  "assets",
  "storyboard",
  "motion",
  "assembly",
  "audio",
  "mix",
  "export",
] as const;

export type WorkbenchStepId = (typeof WORKBENCH_STEP_IDS)[number];

export type WorkspaceRoute =
  | { view: "home" }
  | { view: "library" }
  | { view: "settings" }
  | { view: "project"; projectId: string; stepId?: WorkbenchStepId }
  | { view: "series"; seriesId: string }
  | { view: "series-episode"; seriesId: string; episodeId: string; stepId?: WorkbenchStepId };

const WORKBENCH_STEP_SET = new Set<string>(WORKBENCH_STEP_IDS);

export function normalizeWorkbenchStep(value: string | undefined | null): WorkbenchStepId | undefined {
  if (!value) return undefined;
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  if (normalized === "qa" || normalized === "qa_export") {
    return "export";
  }
  return WORKBENCH_STEP_SET.has(normalized) ? normalized as WorkbenchStepId : undefined;
}

export function parseWorkspaceHash(hash: string): WorkspaceRoute {
  const normalizedHash = hash || "#/";

  const seriesEpisodeMatch = normalizedHash.match(/^#\/series\/([^/]+)\/episode\/([^/]+)(?:\/step\/([^/]+))?$/);
  if (seriesEpisodeMatch) {
    return {
      view: "series-episode",
      seriesId: decodeURIComponent(seriesEpisodeMatch[1]),
      episodeId: decodeURIComponent(seriesEpisodeMatch[2]),
      stepId: normalizeWorkbenchStep(seriesEpisodeMatch[3] ? decodeURIComponent(seriesEpisodeMatch[3]) : undefined),
    };
  }

  const seriesMatch = normalizedHash.match(/^#\/series\/([^/]+)$/);
  if (seriesMatch) {
    return {
      view: "series",
      seriesId: decodeURIComponent(seriesMatch[1]),
    };
  }

  const projectMatch = normalizedHash.match(/^#\/project\/([^/]+)(?:\/step\/([^/]+))?$/);
  if (projectMatch) {
    return {
      view: "project",
      projectId: decodeURIComponent(projectMatch[1]),
      stepId: normalizeWorkbenchStep(projectMatch[2] ? decodeURIComponent(projectMatch[2]) : undefined),
    };
  }

  if (normalizedHash === "#/library") {
    return { view: "library" };
  }

  if (normalizedHash === "#/settings") {
    return { view: "settings" };
  }

  return { view: "home" };
}

export function buildProjectWorkbenchHash(projectId: string, stepId?: WorkbenchStepId): string {
  const base = `#/project/${encodeURIComponent(projectId)}`;
  return stepId ? `${base}/step/${stepId}` : base;
}

export function buildSeriesEpisodeWorkbenchHash(
  seriesId: string,
  episodeId: string,
  stepId?: WorkbenchStepId
): string {
  const base = `#/series/${encodeURIComponent(seriesId)}/episode/${encodeURIComponent(episodeId)}`;
  return stepId ? `${base}/step/${stepId}` : base;
}
