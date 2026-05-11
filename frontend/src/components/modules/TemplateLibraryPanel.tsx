"use client";

import { useEffect, useMemo, useState } from "react";
import {
    AlertCircle,
    Clapperboard,
    CopyPlus,
    FileCode2,
    Loader2,
    PlayCircle,
    RefreshCw,
    ShieldCheck,
} from "lucide-react";
import { api, type FilmTemplateCatalog, type PilotSampleTemplate, type SeriesProductionTemplate } from "@/lib/api";
import {
    getSeriesTemplateStats,
    getTemplateCatalogStats,
    hasRequiredDramaTemplates,
    sortPilotTemplates,
} from "@/lib/filmTemplates";

interface TemplateLibraryPanelProps {
    onCreated?: () => Promise<void> | void;
}

interface TemplatePilotCardProps {
    sample: PilotSampleTemplate;
    creatingId: string | null;
    onCreate: (sample: PilotSampleTemplate) => void;
}

interface TemplateSeriesCardProps {
    blueprint: SeriesProductionTemplate;
    creatingId: string | null;
    onCreate: (blueprint: SeriesProductionTemplate) => void;
}

/**
 * Renders one pilot sample template with its validation objective and create action.
 */
function TemplatePilotCard({ sample, creatingId, onCreate }: TemplatePilotCardProps) {
    const isCreating = creatingId === sample.sample_id;

    return (
        <article className="rounded-lg border border-gray-700/70 bg-gray-950/60 p-4">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <p className="text-[11px] font-mono uppercase tracking-wide text-emerald-300">
                        {sample.genre}
                    </p>
                    <h3 className="mt-1 text-base font-display font-bold text-white">
                        {sample.title}
                    </h3>
                </div>
                <span className="shrink-0 rounded-md bg-emerald-500/10 px-2 py-1 text-xs font-semibold text-emerald-200">
                    {sample.target_duration_seconds}s
                </span>
            </div>

            <div className="mt-3 space-y-2 text-sm text-gray-300">
                <p>{sample.audience_hook}</p>
                <p className="text-xs text-gray-500">{sample.production_risk}</p>
                <p className="text-xs text-amber-200">{sample.success_metric}</p>
            </div>

            <button
                onClick={() => onCreate(sample)}
                disabled={Boolean(creatingId)}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-500/15 px-3 py-2 text-sm font-medium text-emerald-100 transition-colors hover:bg-emerald-500/25 disabled:cursor-not-allowed disabled:opacity-60"
            >
                {isCreating ? <Loader2 size={15} className="animate-spin" /> : <CopyPlus size={15} />}
                创建样片
            </button>
        </article>
    );
}

/**
 * Renders one multi-episode validation blueprint with continuity asset counts.
 */
function TemplateSeriesCard({ blueprint, creatingId, onCreate }: TemplateSeriesCardProps) {
    const stats = getSeriesTemplateStats(blueprint);
    const isCreating = creatingId === blueprint.id;

    return (
        <article className="rounded-lg border border-sky-500/30 bg-sky-950/20 p-4">
            <div className="flex items-start justify-between gap-3">
                <div>
                    <p className="text-[11px] font-mono uppercase tracking-wide text-sky-300">
                        {stats.format}
                    </p>
                    <h3 className="mt-1 text-lg font-display font-bold text-white">
                        {blueprint.title}
                    </h3>
                </div>
                <span className="shrink-0 rounded-md bg-sky-500/15 px-2 py-1 text-xs font-semibold text-sky-100">
                    {stats.episodeCount} 集
                </span>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-gray-300">
                <span className="rounded-md bg-white/[0.04] px-2 py-1">角色 {stats.characterCount}</span>
                <span className="rounded-md bg-white/[0.04] px-2 py-1">场景 {stats.sceneCount}</span>
                <span className="rounded-md bg-white/[0.04] px-2 py-1">道具 {stats.propCount}</span>
                <span className="rounded-md bg-white/[0.04] px-2 py-1">服装 {stats.costumeCount}</span>
            </div>

            {stats.targetDurationSeconds ? (
                <p className="mt-3 text-xs text-gray-400">
                    单集目标 {stats.targetDurationSeconds}s · backend {blueprint.backend}
                </p>
            ) : null}

            <button
                onClick={() => onCreate(blueprint)}
                disabled={Boolean(creatingId)}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-sky-500/15 px-3 py-2 text-sm font-medium text-sky-100 transition-colors hover:bg-sky-500/25 disabled:cursor-not-allowed disabled:opacity-60"
            >
                {isCreating ? <Loader2 size={15} className="animate-spin" /> : <PlayCircle size={15} />}
                创建 5 集系列
            </button>
        </article>
    );
}

/**
 * Shows repository-backed AI mini-drama templates on the Studio home page.
 */
export default function TemplateLibraryPanel({ onCreated }: TemplateLibraryPanelProps) {
    const [catalog, setCatalog] = useState<FilmTemplateCatalog | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [creatingId, setCreatingId] = useState<string | null>(null);

    const pilotSamples = useMemo(
        () => sortPilotTemplates(catalog?.pilot_samples.samples || []),
        [catalog],
    );
    const seriesBlueprints = catalog?.series_blueprints || [];
    const stats = getTemplateCatalogStats(catalog);
    const hasRequiredTemplates = hasRequiredDramaTemplates(catalog);

    /**
     * Loads the template catalog from the backend and surfaces routing failures.
     */
    const loadTemplates = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const nextCatalog = await api.getFilmTemplates();
            setCatalog(nextCatalog);
        } catch (loadError) {
            console.error("Failed to load Film templates:", loadError);
            setError("模板目录加载失败");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        void loadTemplates();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    /**
     * Creates a draft project from one pilot template and opens its QA step.
     */
    const handleCreatePilot = async (sample: PilotSampleTemplate) => {
        setCreatingId(sample.sample_id);
        try {
            const result = await api.createProjectFromPilotTemplate(sample.sample_id);
            await onCreated?.();
            window.location.hash = result.next_hash;
        } catch (createError) {
            console.error("Failed to create pilot template project:", createError);
            setError("样片创建失败");
        } finally {
            setCreatingId(null);
        }
    };

    /**
     * Creates a five-episode draft series from one validation blueprint.
     */
    const handleCreateSeries = async (blueprint: SeriesProductionTemplate) => {
        setCreatingId(blueprint.id);
        try {
            const result = await api.createSeriesFromTemplate(blueprint.id);
            await onCreated?.();
            window.location.hash = result.next_hash;
        } catch (createError) {
            console.error("Failed to create series template:", createError);
            setError("系列模板创建失败");
        } finally {
            setCreatingId(null);
        }
    };

    return (
        <section className="mb-8 border-b border-gray-800/80 pb-8" aria-label="AI 漫剧模板中心">
            <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                <div>
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span className="inline-flex items-center gap-1 rounded-md bg-white/10 px-2 py-1 text-xs font-medium text-gray-200">
                            <ShieldCheck size={13} />
                            AIDrama Studio
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-100">
                            <Clapperboard size={13} />
                            {stats.pilotSampleCount} 个样片 · {stats.totalEpisodeCount} 集验证
                        </span>
                    </div>
                    <h2 className="text-2xl font-display font-bold text-white">AI 漫剧模板中心</h2>
                </div>

                <button
                    onClick={loadTemplates}
                    disabled={isLoading}
                    className="flex items-center justify-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
                >
                    <RefreshCw size={15} className={isLoading ? "animate-spin" : ""} />
                    刷新模板
                </button>
            </div>

            {error ? (
                <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">
                    <AlertCircle size={16} />
                    {error}
                </div>
            ) : null}

            {isLoading ? (
                <div className="grid grid-cols-1 gap-3 lg:grid-cols-4">
                    {[0, 1, 2, 3].map((index) => (
                        <div key={index} className="h-40 rounded-lg border border-gray-800 bg-white/[0.03] animate-pulse" />
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-3 lg:grid-cols-4">
                    {pilotSamples.map((sample) => (
                        <TemplatePilotCard
                            key={sample.sample_id}
                            sample={sample}
                            creatingId={creatingId}
                            onCreate={handleCreatePilot}
                        />
                    ))}

                    {seriesBlueprints.map((blueprint) => (
                        <TemplateSeriesCard
                            key={blueprint.id}
                            blueprint={blueprint}
                            creatingId={creatingId}
                            onCreate={handleCreateSeries}
                        />
                    ))}
                </div>
            )}

            {hasRequiredTemplates ? (
                <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                    <FileCode2 size={14} />
                    samples/pilot_samples · samples/series_production
                </div>
            ) : null}
        </section>
    );
}
