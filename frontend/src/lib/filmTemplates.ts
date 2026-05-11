import type {
    FilmTemplateCatalog,
    PilotSampleTemplate,
    SeriesProductionTemplate,
} from "@/lib/api";

export interface SeriesTemplateStats {
    episodeCount: number;
    characterCount: number;
    sceneCount: number;
    propCount: number;
    costumeCount: number;
    targetDurationSeconds: number | null;
    format: string;
}

export interface TemplateCatalogStats {
    pilotSampleCount: number;
    seriesBlueprintCount: number;
    totalEpisodeCount: number;
}

/**
 * Calculates stable counts for the visible template center.
 * @param catalog Template catalog returned by the Film Core backend.
 * @returns Counts used by dashboard badges and tests.
 */
export function getTemplateCatalogStats(catalog: FilmTemplateCatalog | null): TemplateCatalogStats {
    if (!catalog) {
        return {
            pilotSampleCount: 0,
            seriesBlueprintCount: 0,
            totalEpisodeCount: 0,
        };
    }

    return {
        pilotSampleCount: catalog.pilot_samples.samples.length,
        seriesBlueprintCount: catalog.series_blueprints.length,
        totalEpisodeCount: catalog.series_blueprints.reduce(
            (total, blueprint) => total + blueprint.episodes.length,
            0,
        ),
    };
}

/**
 * Extracts production stats from one series validation blueprint.
 * @param blueprint Series production template from the catalog.
 * @returns Asset and duration stats for the UI.
 */
export function getSeriesTemplateStats(blueprint: SeriesProductionTemplate): SeriesTemplateStats {
    return {
        episodeCount: blueprint.episodes.length,
        characterCount: blueprint.characters?.length || 0,
        sceneCount: blueprint.scenes?.length || 0,
        propCount: blueprint.props?.length || 0,
        costumeCount: blueprint.costumes?.length || 0,
        targetDurationSeconds: Number(blueprint.metadata?.target_episode_duration_seconds) || null,
        format: String(blueprint.metadata?.format || "vertical_9_16"),
    };
}

/**
 * Sorts pilot samples by duration and stable id for deterministic rendering.
 * @param samples Pilot samples from the catalog.
 * @returns A new sorted sample list.
 */
export function sortPilotTemplates(samples: PilotSampleTemplate[]): PilotSampleTemplate[] {
    return [...samples].sort((left, right) => {
        if (left.target_duration_seconds !== right.target_duration_seconds) {
            return left.target_duration_seconds - right.target_duration_seconds;
        }
        return left.sample_id.localeCompare(right.sample_id);
    });
}

/**
 * Checks whether the catalog has the expected D7 validation template coverage.
 * @param catalog Template catalog returned by the backend.
 * @returns True when three pilot samples and one five-episode blueprint are present.
 */
export function hasRequiredDramaTemplates(catalog: FilmTemplateCatalog | null): boolean {
    if (!catalog) return false;
    const stats = getTemplateCatalogStats(catalog);
    return (
        stats.pilotSampleCount >= 3 &&
        catalog.series_blueprints.some((blueprint) => blueprint.episodes.length >= 5)
    );
}
