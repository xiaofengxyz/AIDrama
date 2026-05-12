"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
    AlertTriangle,
    CheckCircle2,
    ClipboardCheck,
    Database,
    Download,
    FileCode2,
    Film,
    Gauge,
    GitBranch,
    ListChecks,
    Play,
    RefreshCw,
    Repeat2,
    Route,
    ShieldCheck,
    SlidersHorizontal,
    Upload,
} from "lucide-react";
import clsx from "clsx";
import { api, type FilmPipelineRunResponse, type WorkflowPromptSwitchesResponse, type WorkflowStatePayload } from "@/lib/api";
import {
    buildFilmPipelinePayload,
    collectLedgerShotRuns,
    evaluateFilmEngineStages,
    getFilmEngineMetrics,
    type FilmEngineStageId,
} from "@/lib/filmEngine";
import { getAssetUrl } from "@/lib/utils";
import { useProjectStore } from "@/store/projectStore";

const stageIcons: Record<FilmEngineStageId, any> = {
    runtime: Gauge,
    director_dsl: FileCode2,
    shot_graph: GitBranch,
    prompt_compiler: ClipboardCheck,
    character_registry: Database,
    scene_registry: Route,
    qa_engine: ShieldCheck,
    retry_engine: Repeat2,
    film_state_engine: ListChecks,
};

const formatNumber = (value: number, digits = 0) =>
    Number.isFinite(value) ? value.toFixed(digits) : "0";

export default function FilmEngineControlRoom() {
    const currentProject = useProjectStore((state) => state.currentProject);
    const [runResult, setRunResult] = useState<FilmPipelineRunResponse | null>(null);
    const [runError, setRunError] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [exportUrl, setExportUrl] = useState<string | null>(currentProject?.merged_video_url || null);
    const [exportError, setExportError] = useState<string | null>(null);
    const [exportMode, setExportMode] = useState<string | null>(currentProject?.merged_video_url ? "video" : null);
    const [exportWarnings, setExportWarnings] = useState<string[]>([]);
    const [exportActions, setExportActions] = useState<string[]>([]);
    const [workflowState, setWorkflowState] = useState<WorkflowStatePayload | null>(null);
    const [workflowError, setWorkflowError] = useState<string | null>(null);
    const [promptSwitches, setPromptSwitches] = useState<WorkflowPromptSwitchesResponse | null>(null);
    const [promptSwitchError, setPromptSwitchError] = useState<string | null>(null);
    const [isLoadingPromptSwitches, setIsLoadingPromptSwitches] = useState(false);
    const [resolution, setResolution] = useState("1080p");
    const [format, setFormat] = useState("mp4");
    const [subtitles, setSubtitles] = useState("burn-in");

    const payload = useMemo(
        () => currentProject ? buildFilmPipelinePayload(currentProject) : null,
        [currentProject]
    );

    const stages = useMemo(() => evaluateFilmEngineStages(runResult), [runResult]);
    const metrics = useMemo(() => getFilmEngineMetrics(runResult), [runResult]);
    const ledgerRuns = useMemo(() => collectLedgerShotRuns(runResult), [runResult]);
    const qaReports = runResult?.film_run?.qa_reports || [];
    const finalClips = runResult?.final_edit?.clips || [];

    const refreshWorkflow = useCallback(async (projectId: string) => {
        setWorkflowError(null);
        try {
            const state = await api.getProjectWorkflow(projectId);
            setWorkflowState(state);
        } catch (error: any) {
            setWorkflowError(error?.message || "Workflow state failed");
        }
    }, []);

    const refreshPromptSwitches = useCallback(async () => {
        setIsLoadingPromptSwitches(true);
        setPromptSwitchError(null);
        try {
            const switches = await api.getWorkflowPromptSwitches();
            setPromptSwitches(switches);
        } catch (error: any) {
            setPromptSwitchError(error?.message || "Workflow switches failed");
        } finally {
            setIsLoadingPromptSwitches(false);
        }
    }, []);

    const runDryRun = useCallback(async () => {
        if (!payload) return;
        setIsRunning(true);
        setRunError(null);
        try {
            const result = await api.runFilmPipeline(payload);
            setRunResult(result);
            if (currentProject?.id) {
                void refreshWorkflow(currentProject.id);
            }
        } catch (error: any) {
            setRunError(error?.response?.data?.detail || error?.message || "Film Engine run failed");
        } finally {
            setIsRunning(false);
        }
    }, [payload, currentProject?.id, refreshWorkflow]);

    useEffect(() => {
        setExportUrl(currentProject?.merged_video_url || null);
        setExportMode(currentProject?.merged_video_url ? "video" : null);
        setExportWarnings([]);
        setExportActions([]);
        setWorkflowState(null);
        setRunResult(null);
        setRunError(null);
        if (currentProject?.id) {
            void refreshWorkflow(currentProject.id);
        }
    }, [currentProject?.id, currentProject?.merged_video_url, refreshWorkflow]);

    useEffect(() => {
        if (payload) {
            void runDryRun();
        }
    }, [payload?.graph_id, runDryRun]);

    useEffect(() => {
        void refreshPromptSwitches();
    }, [refreshPromptSwitches]);

    const handleExport = async () => {
        if (!currentProject) return;
        setIsExporting(true);
        setExportError(null);
        setExportWarnings([]);
        setExportActions([]);
        try {
            const result = await api.exportProject(currentProject.id, {
                resolution,
                format,
                subtitles,
                allow_package_fallback: true,
            });
            setExportUrl(result.url);
            setExportMode(result.mode || "video");
            setExportWarnings(result.warnings || []);
            setExportActions(result.action_required || []);
            if (result.workflow_state) {
                setWorkflowState(result.workflow_state);
            }
        } catch (error: any) {
            setExportError(error?.message || "Export failed");
        } finally {
            setIsExporting(false);
        }
    };

    if (!currentProject) {
        return (
            <div className="h-full flex items-center justify-center text-gray-500">
                No project loaded
            </div>
        );
    }

    return (
        <div className="h-full text-white overflow-hidden bg-[#08090b]/80">
            <div className="h-full grid grid-cols-[320px_minmax(0,1fr)]">
                <aside className="border-r border-white/10 bg-black/25 flex flex-col min-h-0">
                    <div className="p-5 border-b border-white/10">
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <h2 className="text-lg font-display font-bold flex items-center gap-2">
                                    <Film size={18} className="text-primary" />
                                    Film Engine
                                </h2>
                                <p className="text-xs text-gray-500 mt-1 truncate">{currentProject.title}</p>
                            </div>
                            <button
                                onClick={runDryRun}
                                disabled={isRunning}
                                className="h-9 w-9 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-300 disabled:opacity-50"
                                title="Run dry-run QA"
                            >
                                {isRunning ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} />}
                            </button>
                        </div>
                    </div>

                    <div className="p-4 space-y-2 overflow-y-auto">
                        {stages.map((stage) => {
                            const Icon = stageIcons[stage.id];
                            const passed = stage.status === "passed";
                            const attention = stage.status === "attention";
                            return (
                                <div
                                    key={stage.id}
                                    className={clsx(
                                        "rounded-lg border p-3 transition-colors",
                                        passed && "bg-emerald-500/[0.08] border-emerald-500/25",
                                        attention && "bg-amber-500/[0.08] border-amber-500/25",
                                        stage.status === "implemented" && "bg-white/[0.04] border-white/10"
                                    )}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={clsx(
                                            "h-8 w-8 rounded-md flex items-center justify-center border",
                                            passed ? "text-emerald-300 border-emerald-500/30 bg-emerald-500/10" :
                                                attention ? "text-amber-300 border-amber-500/30 bg-amber-500/10" :
                                                    "text-gray-400 border-white/10 bg-white/5"
                                        )}>
                                            <Icon size={15} />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="flex items-center justify-between gap-2">
                                                <span className="text-sm font-semibold truncate">{stage.order}. {stage.label}</span>
                                                {passed ? (
                                                    <CheckCircle2 size={14} className="text-emerald-300 flex-shrink-0" />
                                                ) : attention ? (
                                                    <AlertTriangle size={14} className="text-amber-300 flex-shrink-0" />
                                                ) : (
                                                    <span className="text-[10px] text-gray-400 border border-white/10 rounded px-1.5 py-0.5">Ready</span>
                                                )}
                                            </div>
                                            <div className="mt-1 text-[11px] text-gray-500 leading-snug">{stage.contract}</div>
                                            <div className="mt-2 text-[11px] text-gray-300 leading-snug">{stage.detail}</div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </aside>

                <section className="min-w-0 min-h-0 flex flex-col">
                    <header className="border-b border-white/10 bg-black/20 p-5">
                        <div className="flex flex-wrap items-center justify-between gap-4">
                            <div>
                                <h1 className="text-xl font-display font-bold">Industrial QA & Export</h1>
                                <div className="text-xs text-gray-500 mt-1">
                                    {runResult?.metadata?.pipeline_version || "film_production_pipeline.v1"} · {runResult?.metadata?.backend || "dry_run"}
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={runDryRun}
                                    disabled={isRunning}
                                    className="inline-flex items-center gap-2 h-9 px-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-gray-200 disabled:opacity-50"
                                >
                                    <RefreshCw size={15} className={isRunning ? "animate-spin" : ""} />
                                    Dry Run
                                </button>
                            </div>
                        </div>

                        {runError && (
                            <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                                {runError}
                            </div>
                        )}
                        {workflowError && (
                            <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
                                {workflowError}
                            </div>
                        )}
                    </header>

                    <div className="flex-1 overflow-y-auto p-5 space-y-5">
                        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-3">
                            {[
                                ["Beats", metrics.beats],
                                ["Shots", metrics.shots],
                                ["Accepted", metrics.acceptedShots],
                                ["Failed", metrics.failedShots],
                                ["Attempts", metrics.totalAttempts],
                                ["Retries", metrics.retryAttempts],
                                ["QA", formatNumber(metrics.qaScore, 2)],
                                ["Duration", `${formatNumber(metrics.totalDuration, 1)}s`],
                            ].map(([label, value]) => (
                                <div key={label} className="rounded-lg border border-white/10 bg-white/[0.04] p-3">
                                    <div className="text-[10px] uppercase tracking-wide text-gray-500">{label}</div>
                                    <div className="text-xl font-semibold mt-1">{value}</div>
                                </div>
                            ))}
                        </div>

                        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.2fr)_360px] gap-5">
                            <div className="space-y-5 min-w-0">
                                {workflowState && (
                                    <WorkflowReadiness workflowState={workflowState} />
                                )}

                                <WorkflowSwitchPanel
                                    data={promptSwitches}
                                    error={promptSwitchError}
                                    isLoading={isLoadingPromptSwitches}
                                    onRefresh={refreshPromptSwitches}
                                />

                                <div className="rounded-lg border border-white/10 bg-black/20">
                                    <div className="h-11 border-b border-white/10 px-4 flex items-center justify-between">
                                        <h3 className="text-sm font-semibold flex items-center gap-2">
                                            <GitBranch size={15} className="text-sky-300" />
                                            Graph Continuity
                                        </h3>
                                        <span className="text-xs text-gray-500">{runResult?.story_graph?.graph_id || payload?.graph_id}</span>
                                    </div>
                                    <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                                        <PipelineArtifact
                                            label="Story Graph"
                                            value={`${runResult?.story_graph?.beats?.length || 0} beat(s)`}
                                            detail={runResult?.story_graph?.metadata?.builder_version as string || "story_graph.v1"}
                                        />
                                        <PipelineArtifact
                                            label="Director Program"
                                            value={`${runResult?.director_program?.shots?.length || 0} shot(s)`}
                                            detail={runResult?.director_program?.metadata?.planner_version as string || "director_planner.v1"}
                                        />
                                        <PipelineArtifact
                                            label="Final Edit"
                                            value={`${finalClips.length} clip(s)`}
                                            detail={`${metrics.unresolvedShots} unresolved`}
                                        />
                                    </div>
                                </div>

                                <div className="rounded-lg border border-white/10 bg-black/20">
                                    <div className="h-11 border-b border-white/10 px-4 flex items-center justify-between">
                                        <h3 className="text-sm font-semibold flex items-center gap-2">
                                            <ShieldCheck size={15} className="text-emerald-300" />
                                            QA Reports
                                        </h3>
                                        <span className="text-xs text-gray-500">threshold 0.82</span>
                                    </div>
                                    <div className="divide-y divide-white/5">
                                        {qaReports.length > 0 ? qaReports.map((report: any) => (
                                            <div key={report.shot_id} className="p-4 flex items-start justify-between gap-4">
                                                <div className="min-w-0">
                                                    <div className="font-mono text-xs text-gray-300">{report.shot_id}</div>
                                                    <div className="text-sm text-gray-400 mt-1">
                                                        {(report.findings || []).length ? report.findings.join(", ") : "No findings"}
                                                    </div>
                                                </div>
                                                <span className={clsx(
                                                    "text-sm font-semibold",
                                                    report.score >= report.threshold ? "text-emerald-300" : "text-amber-300"
                                                )}>
                                                    {Number(report.score || 0).toFixed(2)}
                                                </span>
                                            </div>
                                        )) : (
                                            <div className="p-5 text-sm text-gray-500">No QA report yet</div>
                                        )}
                                    </div>
                                </div>

                                <div className="rounded-lg border border-white/10 bg-black/20">
                                    <div className="h-11 border-b border-white/10 px-4 flex items-center justify-between">
                                        <h3 className="text-sm font-semibold flex items-center gap-2">
                                            <Database size={15} className="text-cyan-300" />
                                            Generation Ledger
                                        </h3>
                                        <span className="text-xs text-gray-500">${formatNumber(metrics.costEstimate, 4)}</span>
                                    </div>
                                    <div className="divide-y divide-white/5">
                                        {ledgerRuns.length > 0 ? ledgerRuns.map((run: any) => (
                                            <div key={run.shot_id} className="p-4 grid grid-cols-[1fr_auto] gap-4">
                                                <div className="min-w-0">
                                                    <div className="font-mono text-xs text-gray-300">{run.shot_id}</div>
                                                    <div className="text-xs text-gray-500 mt-1 truncate">
                                                        {run.selected_output_uri || "No selected output"}
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-sm text-gray-200">{run.status}</div>
                                                    <div className="text-xs text-gray-500">{run.attempts?.length || 0} attempt(s)</div>
                                                </div>
                                            </div>
                                        )) : (
                                            <div className="p-5 text-sm text-gray-500">No ledger yet</div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-5">
                                <div className="rounded-lg border border-white/10 bg-black/20">
                                    <div className="h-11 border-b border-white/10 px-4 flex items-center gap-2">
                                        <SlidersHorizontal size={15} className="text-primary" />
                                        <h3 className="text-sm font-semibold">Render Package</h3>
                                    </div>
                                    <div className="p-4 space-y-4">
                                        <SegmentedControl
                                            label="Resolution"
                                            value={resolution}
                                            options={["1080p", "4K"]}
                                            onChange={setResolution}
                                        />
                                        <SegmentedControl
                                            label="Format"
                                            value={format}
                                            options={["mp4", "mov", "gif"]}
                                            onChange={setFormat}
                                        />
                                        <SegmentedControl
                                            label="Subtitles"
                                            value={subtitles}
                                            options={["burn-in", "srt", "none"]}
                                            onChange={setSubtitles}
                                        />
                                        <button
                                            onClick={handleExport}
                                            disabled={isExporting}
                                            className="w-full h-10 rounded-lg bg-primary hover:bg-primary/90 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                                        >
                                            {isExporting ? <RefreshCw size={16} className="animate-spin" /> : <Upload size={16} />}
                                            {isExporting ? "Rendering" : "Start Render"}
                                        </button>
                                        {exportMode && (
                                            <div className="text-xs text-gray-400">
                                                Output mode: <span className="text-gray-200">{exportMode === "render_package" ? "Render package" : "Video"}</span>
                                            </div>
                                        )}
                                        {exportWarnings.length > 0 && (
                                            <div className="space-y-1 text-xs text-amber-200 border border-amber-500/30 bg-amber-500/10 rounded-lg p-3">
                                                {exportWarnings.map((warning) => (
                                                    <div key={warning}>{warning}</div>
                                                ))}
                                            </div>
                                        )}
                                        {exportActions.length > 0 && (
                                            <div className="space-y-1 text-xs text-gray-300 border border-white/10 bg-white/[0.04] rounded-lg p-3">
                                                {exportActions.slice(0, 3).map((action) => (
                                                    <div key={action}>{action}</div>
                                                ))}
                                            </div>
                                        )}
                                        {exportError && (
                                            <div className="text-sm text-red-300 border border-red-500/30 bg-red-500/10 rounded-lg p-3">
                                                {exportError}
                                            </div>
                                        )}
                                        {exportUrl && (
                                            <a
                                                href={getAssetUrl(exportUrl)}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="w-full h-10 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-200 font-semibold flex items-center justify-center gap-2"
                                            >
                                                <Download size={16} />
                                                {exportMode === "render_package" ? "Download Package" : "Download"}
                                            </a>
                                        )}
                                    </div>
                                </div>

                                <div className="rounded-lg border border-white/10 bg-black/20">
                                    <div className="h-11 border-b border-white/10 px-4 flex items-center gap-2">
                                        <ListChecks size={15} className="text-amber-300" />
                                        <h3 className="text-sm font-semibold">Final Edit</h3>
                                    </div>
                                    <div className="p-4 space-y-3">
                                        {finalClips.length > 0 ? finalClips.map((clip: any) => (
                                            <div key={clip.clip_id} className="rounded-lg bg-white/[0.04] border border-white/10 p-3">
                                                <div className="flex items-center justify-between gap-3">
                                                    <span className="font-mono text-xs text-gray-300">{clip.clip_id}</span>
                                                    <span className="text-xs text-gray-500">{Number(clip.duration || 0).toFixed(1)}s</span>
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1 truncate">{clip.output_uri}</div>
                                            </div>
                                        )) : (
                                            <div className="text-sm text-gray-500">No final edit clips yet</div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}

function WorkflowReadiness({ workflowState }: { workflowState: WorkflowStatePayload }) {
    const summary = workflowState.summary || {};
    return (
        <div className="rounded-lg border border-white/10 bg-black/20">
            <div className="h-11 border-b border-white/10 px-4 flex items-center justify-between">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Route size={15} className="text-violet-300" />
                    CineForge Workflow
                </h3>
                <span className="text-xs text-gray-500">{summary.recommended_render_mode || "dry-run"}</span>
            </div>
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {workflowState.stages.map((stage) => {
                    const passed = stage.status === "passed";
                    const blocked = stage.status === "blocked";
                    const ready = stage.status === "ready";
                    return (
                        <div
                            key={stage.id}
                            className={clsx(
                                "rounded-lg border p-3 bg-white/[0.04]",
                                passed && "border-emerald-500/25",
                                ready && "border-sky-500/25",
                                blocked && "border-red-500/25",
                                !passed && !ready && !blocked && "border-amber-500/25"
                            )}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                    <div className="text-sm font-semibold truncate">{stage.order}. {stage.label}</div>
                                    <div className="text-[11px] text-gray-500 mt-1 truncate">{stage.required_artifact}</div>
                                </div>
                                <span className={clsx(
                                    "text-[10px] uppercase rounded px-1.5 py-0.5 border",
                                    passed && "text-emerald-200 border-emerald-500/30 bg-emerald-500/10",
                                    ready && "text-sky-200 border-sky-500/30 bg-sky-500/10",
                                    blocked && "text-red-200 border-red-500/30 bg-red-500/10",
                                    !passed && !ready && !blocked && "text-amber-200 border-amber-500/30 bg-amber-500/10"
                                )}>
                                    {stage.status}
                                </span>
                            </div>
                            <div className="mt-3 h-1.5 rounded-full bg-white/10 overflow-hidden">
                                <div
                                    className={clsx(
                                        "h-full rounded-full",
                                        passed ? "bg-emerald-400" : ready ? "bg-sky-400" : blocked ? "bg-red-400" : "bg-amber-400"
                                    )}
                                    style={{ width: `${Math.round((stage.progress || 0) * 100)}%` }}
                                />
                            </div>
                            <div className="text-[11px] text-gray-400 mt-2 line-clamp-2">{stage.next_action}</div>
                            {stage.model_recommendations?.[0] && (
                                <div className="text-[11px] text-gray-500 mt-2 truncate">
                                    {stage.model_recommendations[0].provider}: {stage.model_recommendations[0].model}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function WorkflowSwitchPanel({
    data,
    error,
    isLoading,
    onRefresh,
}: {
    data: WorkflowPromptSwitchesResponse | null;
    error: string | null;
    isLoading: boolean;
    onRefresh: () => void;
}) {
    const summary = data?.execution_plan?.summary || {};
    const steps = data?.execution_plan?.steps || [];
    const stepByModule = new Map(steps.map((step: any) => [step.module_id, step]));

    return (
        <div className="rounded-lg border border-white/10 bg-black/20">
            <div className="h-11 border-b border-white/10 px-4 flex items-center justify-between gap-3">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                    <SlidersHorizontal size={15} className="text-purple-300" />
                    Workflow Switches
                </h3>
                <button
                    onClick={onRefresh}
                    disabled={isLoading}
                    className="h-8 px-2.5 rounded-md border border-white/10 bg-white/5 hover:bg-white/10 text-xs text-gray-200 flex items-center gap-1.5 disabled:opacity-50"
                    title="Refresh workflow_switch state"
                >
                    <RefreshCw size={13} className={isLoading ? "animate-spin" : ""} />
                    Refresh Switches
                </button>
            </div>
            <div className="p-4 space-y-3">
                <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                    <span className="rounded border border-white/10 bg-white/[0.04] px-2 py-1">
                        Source: {data?.source || "docs/Codex_Workflow_Prompts"}
                    </span>
                    <span className="rounded border border-emerald-500/20 bg-emerald-500/10 text-emerald-200 px-2 py-1">
                        Auto {summary.auto_modules ?? 0}/{summary.module_count ?? 0}
                    </span>
                    <span className="rounded border border-amber-500/20 bg-amber-500/10 text-amber-200 px-2 py-1">
                        Manual gates {summary.manual_gates ?? 0}
                    </span>
                    {data?.execution_plan?.first_waiting_stage && (
                        <span className="rounded border border-red-500/20 bg-red-500/10 text-red-200 px-2 py-1">
                            Pauses at {data.execution_plan.first_waiting_stage}
                        </span>
                    )}
                </div>

                {error && (
                    <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-2">
                    {(data?.modules || []).map((module) => {
                        const step = stepByModule.get(module.switch.module_id) as any;
                        const waits = Boolean(step?.waits_for_user);
                        const auto = module.switch.auto_advance && !waits;
                        return (
                            <div
                                key={module.switch.module_id}
                                className={clsx(
                                    "rounded-lg border p-3 bg-white/[0.04]",
                                    auto ? "border-emerald-500/25" : "border-amber-500/30"
                                )}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="min-w-0">
                                        <div className="text-xs font-mono text-gray-500">{String(module.order).padStart(2, "0")}</div>
                                        <div className="text-sm font-semibold text-gray-200 truncate">
                                            {module.switch.label || module.title}
                                        </div>
                                    </div>
                                    <span className={clsx(
                                        "text-[10px] rounded px-1.5 py-0.5 border uppercase",
                                        auto
                                            ? "text-emerald-200 border-emerald-500/30 bg-emerald-500/10"
                                            : "text-amber-200 border-amber-500/30 bg-amber-500/10"
                                    )}>
                                        {auto ? "auto" : "manual"}
                                    </span>
                                </div>
                                <div className="mt-2 text-[11px] text-gray-500 truncate">{module.switch.stage_id}</div>
                                <div className="mt-2 flex gap-1 text-[10px] text-gray-400">
                                    <span className={module.switch.auto_advance ? "text-emerald-300" : "text-amber-300"}>
                                        auto_advance={String(module.switch.auto_advance)}
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

function PipelineArtifact({ label, value, detail }: { label: string; value: string; detail: string }) {
    return (
        <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
            <div className="text-[10px] uppercase tracking-wide text-gray-500">{label}</div>
            <div className="text-lg font-semibold mt-2">{value}</div>
            <div className="text-xs text-gray-500 mt-1 truncate">{detail}</div>
        </div>
    );
}

function SegmentedControl({
    label,
    value,
    options,
    onChange,
}: {
    label: string;
    value: string;
    options: string[];
    onChange: (value: string) => void;
}) {
    return (
        <div>
            <div className="text-xs text-gray-500 mb-2">{label}</div>
            <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }}>
                {options.map((option) => (
                    <button
                        key={option}
                        onClick={() => onChange(option)}
                        className={clsx(
                            "h-9 rounded-lg border text-xs font-semibold uppercase transition-colors",
                            value === option
                                ? "bg-white text-black border-white"
                                : "bg-white/5 border-white/10 text-gray-400 hover:text-white hover:bg-white/10"
                        )}
                    >
                        {option}
                    </button>
                ))}
            </div>
        </div>
    );
}
