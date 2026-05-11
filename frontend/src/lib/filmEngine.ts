import type { FilmPipelineRunPayload, FilmPipelineRunResponse } from "@/lib/api";
import type { Character, ImageAsset, Project, Prop, Scene } from "@/store/projectStore";

export type FilmEngineStageId =
    | "runtime"
    | "director_dsl"
    | "shot_graph"
    | "prompt_compiler"
    | "character_registry"
    | "scene_registry"
    | "qa_engine"
    | "retry_engine"
    | "film_state_engine";

export type FilmEngineStageStatus = "implemented" | "passed" | "attention";

export interface FilmEngineStage {
    id: FilmEngineStageId;
    order: number;
    label: string;
    contract: string;
    artifact: string;
}

export interface FilmEngineStageRun extends FilmEngineStage {
    status: FilmEngineStageStatus;
    detail: string;
}

export interface FilmEngineMetrics {
    beats: number;
    shots: number;
    acceptedShots: number;
    failedShots: number;
    totalAttempts: number;
    retryAttempts: number;
    qaScore: number;
    unresolvedShots: number;
    totalDuration: number;
    costEstimate: number;
}

export const FILM_ENGINE_STAGES: FilmEngineStage[] = [
    {
        id: "runtime",
        order: 1,
        label: "Runtime",
        contract: "Runtime backend adapter",
        artifact: "dry_run / vendor adapter boundary",
    },
    {
        id: "director_dsl",
        order: 2,
        label: "Director DSL",
        contract: "Director program",
        artifact: "shot type, framing, movement, lens",
    },
    {
        id: "shot_graph",
        order: 3,
        label: "Shot Graph",
        contract: "Shot graph DAG",
        artifact: "shots, transitions, adjacency",
    },
    {
        id: "prompt_compiler",
        order: 4,
        label: "Prompt Compiler",
        contract: "Compiled prompt",
        artifact: "prompt fingerprint and negative prompt",
    },
    {
        id: "character_registry",
        order: 5,
        label: "Character Registry",
        contract: "Character bible",
        artifact: "locked traits and reference images",
    },
    {
        id: "scene_registry",
        order: 6,
        label: "Scene Registry",
        contract: "Scene bible",
        artifact: "location, lighting, mood continuity",
    },
    {
        id: "qa_engine",
        order: 7,
        label: "QA Engine",
        contract: "QA report",
        artifact: "score, threshold, findings",
    },
    {
        id: "retry_engine",
        order: 8,
        label: "Retry Engine",
        contract: "Retry decision",
        artifact: "attempts and repair notes",
    },
    {
        id: "film_state_engine",
        order: 9,
        label: "Film State Engine",
        contract: "Film state timeline",
        artifact: "continuity locks and selected output",
    },
];

const NON_WORD = /[^a-zA-Z0-9_\-\u4e00-\u9fff]+/g;
const SCRIPT_TAG = /\[(character|prop|costume)=([^\]\s]+)\]/g;

/** Removes empty values and duplicate strings while preserving first-seen order. */
function compact(values: Array<string | undefined | null>): string[] {
    return Array.from(
        new Set(
            values
                .map((value) => value?.trim())
                .filter((value): value is string => Boolean(value))
        )
    );
}

/** Builds a stable Film Core id from free-form Studio values. */
function stableId(value: string | undefined, fallback: string): string {
    const source = value?.trim() || fallback;
    return source.replace(NON_WORD, "_").replace(/^_+|_+$/g, "") || fallback;
}

/** Creates a readable fallback label for assets inferred from script tags. */
function labelFromId(value: string): string {
    return value
        .replace(/[_\-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, (letter) => letter.toUpperCase()) || value;
}

/** Extracts explicit Film Core asset tags from the source script. */
function extractTaggedIds(sourceText: string, tagName: "character" | "prop" | "costume"): string[] {
    const ids: string[] = [];
    SCRIPT_TAG.lastIndex = 0;
    let match = SCRIPT_TAG.exec(sourceText);
    while (match) {
        if (match[1] === tagName) {
            ids.push(stableId(match[2], match[2]));
        }
        match = SCRIPT_TAG.exec(sourceText);
    }
    return compact(ids);
}

/** Returns ids from script tags that are not already covered by Studio assets. */
function missingTaggedIds(sourceText: string, tagName: "character" | "prop" | "costume", knownIds: string[]): string[] {
    const known = new Set(knownIds.map((id) => stableId(id, id)));
    return extractTaggedIds(sourceText, tagName).filter((id) => !known.has(id));
}

/** Returns lightweight character assets declared directly in a script tag. */
function inferredCharactersFromTags(sourceText: string, knownIds: string[]) {
    return missingTaggedIds(sourceText, "character", knownIds).map((id) => ({
        id,
        name: labelFromId(id),
        description: `Character declared by script tag ${id}.`,
        reference_images: [],
        locked_traits: ["script_tagged"],
        continuity_notes: ["Declared in source script before asset generation."],
    }));
}

/** Returns lightweight prop assets declared directly in a script tag. */
function inferredPropsFromTags(sourceText: string, knownIds: string[]) {
    return missingTaggedIds(sourceText, "prop", knownIds).map((id) => ({
        id,
        name: labelFromId(id),
        description: `Prop declared by script tag ${id}.`,
        reference_images: [],
        locked_traits: ["script_tagged"],
        continuity_notes: ["Declared in source script before asset generation."],
    }));
}

/** Returns lightweight costume assets from script tags and character outfits. */
function inferredCostumesFromTags(sourceText: string, outfitValues: string[]) {
    const costumeIds = compact([
        ...extractTaggedIds(sourceText, "costume"),
        ...outfitValues.map((outfit) => stableId(outfit, outfit)),
    ]);
    return costumeIds.map((id) => ({
        id,
        name: labelFromId(id),
        description: `Costume declared by script tag or Studio character outfit ${id}.`,
        reference_images: [],
        locked_traits: ["script_tagged"],
        continuity_notes: ["Derived for Film Core continuity validation."],
    }));
}

/** Selects the active preview image from a Studio image asset. */
function selectedImage(asset?: ImageAsset): string | undefined {
    if (!asset?.variants?.length) return undefined;
    return asset.variants.find((variant) => variant.id === asset.selected_id)?.url || asset.variants[0]?.url;
}

/** Collects every available character reference image for Film Core. */
function characterReferenceImages(character: Character): string[] {
    return compact([
        character.image_url,
        character.avatar_url,
        character.full_body_image_url,
        character.three_view_image_url,
        character.headshot_image_url,
        selectedImage(character.full_body_asset),
        selectedImage(character.three_view_asset),
        selectedImage(character.headshot_asset),
    ]);
}

/** Collects every available scene reference image for Film Core. */
function sceneReferenceImages(scene: Scene): string[] {
    return compact([scene.image_url, selectedImage(scene.image_asset)]);
}

/** Collects every available prop reference image for Film Core. */
function propReferenceImages(prop: Prop): string[] {
    return compact([prop.image_url, selectedImage(prop.image_asset)]);
}

/** Builds source text for Film Core from raw script text or storyboard frames. */
export function buildFilmSourceText(project: Project): string {
    const originalText = project.originalText?.trim();
    if (originalText) return originalText;

    const scenesById = new Map((project.scenes || []).map((scene) => [scene.id, scene]));
    const charactersById = new Map((project.characters || []).map((character) => [character.id, character]));
    const frames = project.frames || [];

    const frameScript = frames
        .map((frame: any, index: number) => {
            const scene = scenesById.get(frame.scene_id);
            const sceneName = scene?.name || frame.scene_id || "studio";
            const speakerId = frame.speaker || frame.character_ids?.[0];
            const speakerName = charactersById.get(speakerId)?.name || speakerId || "Narrator";
            const dialogue = frame.dialogue ? `${speakerName}: ${frame.dialogue}` : "";
            const propTags = (frame.prop_ids || []).map((id: string) => `[prop=${id}]`).join(" ");
            const action = frame.action_description || frame.image_prompt || `Shot ${index + 1}`;
            return compact([
                `INT. ${String(sceneName).toUpperCase()}`,
                dialogue,
                `${action} ${propTags}`.trim(),
            ]).join("\n");
        })
        .join("\n\n")
        .trim();

    if (frameScript) return frameScript;

    return `INT. STUDIO\nNarrator: ${project.title || "Untitled project"} enters Film Engine dry run.`;
}

/** Builds a Film Core dry-run payload from one Studio project. */
export function buildFilmPipelinePayload(project: Project): FilmPipelineRunPayload {
    const scriptText = buildFilmSourceText(project);
    const characters = (project.characters || []).map((character) => ({
        id: stableId(character.id, stableId(character.name, "character")),
        name: character.name || character.id,
        description: character.description || "",
        current_outfit: character.clothing || undefined,
        reference_images: characterReferenceImages(character),
        locked_traits: compact([
            character.locked ? "identity_locked" : undefined,
            character.is_consistent ? "consistency_verified" : undefined,
            character.clothing,
        ]),
        continuity_notes: compact([character.age, character.gender, character.clothing]),
    }));

    const scenes = (project.scenes || []).map((scene) => ({
        id: stableId(scene.id, stableId(scene.name, "scene")),
        location: scene.name || scene.id,
        mood: scene.lighting_mood || scene.description || "",
        lighting: scene.lighting_mood || undefined,
        time_of_day: scene.time_of_day || undefined,
        reference_images: sceneReferenceImages(scene),
        continuity_notes: compact([scene.description, scene.time_of_day, scene.lighting_mood]),
    }));

    const props = (project.props || []).map((prop) => ({
        id: stableId(prop.id, stableId(prop.name, "prop")),
        name: prop.name || prop.id,
        description: prop.description || "",
        reference_images: propReferenceImages(prop),
        locked_traits: compact([prop.locked ? "prop_locked" : undefined]),
        continuity_notes: compact([prop.description]),
    }));
    const allCharacters = [
        ...characters,
        ...inferredCharactersFromTags(scriptText, characters.map((character) => character.id)),
    ];
    const allProps = [
        ...props,
        ...inferredPropsFromTags(scriptText, props.map((prop) => prop.id)),
    ];
    const costumes = inferredCostumesFromTags(
        scriptText,
        compact((project.characters || []).map((character) => character.clothing)),
    );

    return {
        script_text: scriptText,
        graph_id: stableId(`film_${project.id}`, "film_project"),
        source_title: project.title || "Untitled Project",
        backend: "dry_run",
        max_attempts: 2,
        min_score: 0.82,
        characters: allCharacters,
        scenes,
        props: allProps,
        costumes,
        continuity_locks: {
            characters: Object.fromEntries(
                allCharacters
                    .filter((character) => character.locked_traits.length > 0)
                    .map((character) => [character.id, { locked_traits: character.locked_traits }])
            ),
            scenes: Object.fromEntries(
                scenes
                    .filter((scene) => scene.continuity_notes.length > 0)
                    .map((scene) => [scene.id, { continuity_notes: scene.continuity_notes }])
            ),
            props: Object.fromEntries(
                allProps
                    .filter((prop) => prop.locked_traits.length > 0)
                    .map((prop) => [prop.id, { locked_traits: prop.locked_traits }])
            ),
            costumes: Object.fromEntries(
                costumes
                    .filter((costume) => costume.locked_traits.length > 0)
                    .map((costume) => [costume.id, { locked_traits: costume.locked_traits }])
            ),
        },
    };
}

/** Collects ledger shot runs from the Film Core response. */
export function collectLedgerShotRuns(response: FilmPipelineRunResponse | null): any[] {
    if (!response?.generation_ledger?.shot_runs) return [];
    return Object.values(response.generation_ledger.shot_runs);
}

/** Converts the Film Core response into dashboard production metrics. */
export function getFilmEngineMetrics(response: FilmPipelineRunResponse | null): FilmEngineMetrics {
    const summary = response?.film_run?.summary || {};
    const qaSummary = response?.final_edit?.qa_summary || {};
    const qaScore = Number(summary.average_qa_score ?? qaSummary.average_qa_score ?? 0);

    return {
        beats: response?.story_graph?.beats?.length || 0,
        shots: Number(summary.total_shots ?? response?.director_program?.shots?.length ?? 0),
        acceptedShots: Number(summary.accepted_shots ?? 0),
        failedShots: Number(summary.failed_shots ?? 0),
        totalAttempts: Number(summary.total_attempts ?? 0),
        retryAttempts: Number(summary.retry_attempts ?? 0),
        qaScore: Number.isFinite(qaScore) ? qaScore : 0,
        unresolvedShots: response?.final_edit?.unresolved_shots?.length || Number(qaSummary.unresolved_count ?? 0),
        totalDuration: Number(response?.final_edit?.total_duration ?? 0),
        costEstimate: Number(summary.total_cost_estimate ?? 0),
    };
}

/** Evaluates the fixed nine Film Engine stages for the QA control room. */
export function evaluateFilmEngineStages(response: FilmPipelineRunResponse | null): FilmEngineStageRun[] {
    if (!response) {
        return FILM_ENGINE_STAGES.map((stage) => ({
            ...stage,
            status: "implemented",
            detail: "module loaded",
        }));
    }

    const metrics = getFilmEngineMetrics(response);
    const ledgerRuns = collectLedgerShotRuns(response);
    const attempts = ledgerRuns.flatMap((run) => run.attempts || []);
    const qaReports = response.film_run?.qa_reports || [];
    const shotGraphShots = response.film_run?.shot_graph?.shots || [];
    const stateTimeline = response.film_run?.final_state?.timeline || [];

    const stageDetails: Record<FilmEngineStageId, { status: FilmEngineStageStatus; detail: string }> = {
        runtime: {
            status: metrics.failedShots > 0 ? "attention" : "passed",
            detail: `${response.metadata?.backend || "dry_run"} backend, ${metrics.totalAttempts} attempt(s)`,
        },
        director_dsl: {
            status: response.director_program?.shots?.length ? "passed" : "attention",
            detail: `${response.director_program?.shots?.length || 0} director shot(s)`,
        },
        shot_graph: {
            status: shotGraphShots.length === metrics.shots && metrics.shots > 0 ? "passed" : "attention",
            detail: `${shotGraphShots.length} shot node(s), ${response.film_run?.shot_graph?.transitions?.length || 0} transition(s)`,
        },
        prompt_compiler: {
            status: attempts.length > 0 && attempts.every((attempt) => attempt.prompt && attempt.prompt_fingerprint) ? "passed" : "attention",
            detail: `${attempts.length} compiled prompt artifact(s)`,
        },
        character_registry: {
            status: "passed",
            detail: `${Object.keys(response.film_run?.final_state?.character_states || {}).length} tracked character(s)`,
        },
        scene_registry: {
            status: "passed",
            detail: `${Object.keys(response.film_run?.final_state?.scene_states || {}).length} tracked scene(s)`,
        },
        qa_engine: {
            status: qaReports.length === metrics.shots && metrics.unresolvedShots === 0 ? "passed" : "attention",
            detail: `${qaReports.length} QA report(s), score ${metrics.qaScore.toFixed(2)}`,
        },
        retry_engine: {
            status: attempts.length >= metrics.shots ? "passed" : "attention",
            detail: `${metrics.retryAttempts} retry attempt(s), max policy applied`,
        },
        film_state_engine: {
            status: stateTimeline.length === metrics.acceptedShots && metrics.acceptedShots > 0 ? "passed" : "attention",
            detail: `${stateTimeline.length} continuity timeline event(s)`,
        },
    };

    return FILM_ENGINE_STAGES.map((stage) => ({
        ...stage,
        ...stageDetails[stage.id],
    }));
}
