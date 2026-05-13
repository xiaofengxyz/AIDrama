"use client";

import type React from "react";
import { useMemo, useState } from "react";
import { AlertCircle, BookOpen, Boxes, Clapperboard, Loader2, Wand2 } from "lucide-react";
import { api, type AutoDramaRunResponse } from "@/lib/api";

interface OneSentenceDramaPanelProps {
    /** Refreshes the workspace after Auto Drama persists a new series. */
    onCreated?: () => Promise<void> | void;
}

interface EpisodePackageSummary {
    /** Storyboard frames generated for one episode package. */
    storyboard_frames?: unknown[];
    /** Costume assets extracted for one episode package. */
    costumes?: unknown[];
    /** Special effects extracted for one episode package. */
    special_effects?: unknown[];
}

const EPISODE_OPTIONS = [3, 5, 8];

/**
 * Visible producer entry for one-sentence idea -> multi-episode AI drama series.
 */
export default function OneSentenceDramaPanel({ onCreated }: OneSentenceDramaPanelProps) {
    const [title, setTitle] = useState("夜半信号");
    const [seedText, setSeedText] = useState("女调查员接到一通来自十年前死者的电话，电话里的人知道她下一步会去哪里。");
    const [episodeCount, setEpisodeCount] = useState(5);
    const [isRunning, setIsRunning] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<AutoDramaRunResponse | null>(null);

    const packageStats = useMemo(() => {
        const packages = (result?.episode_packages || []) as EpisodePackageSummary[];
        return {
            episodes: packages.length,
            frames: packages.reduce((total, item) => total + (item.storyboard_frames?.length || 0), 0),
            costumes: packages.reduce((total, item) => total + (item.costumes?.length || 0), 0),
            effects: packages.reduce((total, item) => total + (item.special_effects?.length || 0), 0),
        };
    }, [result]);

    /**
     * Runs the dry-run producer flow and asks the backend to persist a Studio series.
     */
    const handleRun = async () => {
        if (!seedText.trim()) {
            setError("请先输入一句故事梗概");
            return;
        }

        setIsRunning(true);
        setError(null);
        setResult(null);
        try {
            const response = await api.runAutoDrama({
                title: title.trim() || "未命名 AI 漫剧",
                seed_text: seedText.trim(),
                target_chapters: episodeCount,
                backend: "dry_run",
                persist_project: true,
                persist_mode: "series",
            });
            setResult(response);
            await onCreated?.();
            if (response.next_hash) {
                window.location.hash = response.next_hash;
            }
        } catch (runError: any) {
            console.error("Failed to run one-sentence Auto Drama:", runError);
            setError(runError?.response?.data?.detail || runError?.message || "一句话生成失败");
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <section className="mb-6 border border-glass-border bg-black/35 p-5 backdrop-blur-md" aria-label="一句话生成 AI 漫剧">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div className="max-w-2xl">
                    <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-gray-300">
                        <span className="inline-flex items-center gap-1 rounded-md bg-primary/15 px-2 py-1 text-primary">
                            <Wand2 size={13} />
                            一句话制片
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-1 text-emerald-100">
                            <Clapperboard size={13} />
                            自动生成系列草稿
                        </span>
                    </div>
                    <h2 className="text-2xl font-display font-bold text-white">一句话生成多集 AI 漫剧</h2>
                    <p className="mt-2 text-sm leading-6 text-gray-400">
                        输入一个故事点，系统会生成小说计划、每集脚本、分镜、角色描述、道具服装、特效生产包，并写入工作区系列。
                    </p>
                </div>

                <div className="grid min-w-[280px] grid-cols-2 gap-2 text-xs text-gray-300 sm:grid-cols-4 xl:w-[520px]">
                    <ProcessChip icon={<BookOpen size={14} />} label="小说计划" value="Novel" />
                    <ProcessChip icon={<Clapperboard size={14} />} label="每集分镜" value="Frames" />
                    <ProcessChip icon={<Boxes size={14} />} label="资产提取" value="Assets" />
                    <ProcessChip icon={<Wand2 size={14} />} label="写入系列" value="Series" />
                </div>
            </div>

            <div className="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-[220px_1fr_auto]">
                <input
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    className="glass-input min-h-[44px] text-sm text-white"
                    placeholder="系列标题"
                />
                <textarea
                    value={seedText}
                    onChange={(event) => setSeedText(event.target.value)}
                    className="glass-input min-h-[44px] resize-none text-sm leading-6 text-white"
                    placeholder="一句话故事梗概，例如：外卖员送到十年前已死客户的家门口。"
                    rows={2}
                />
                <button
                    onClick={handleRun}
                    disabled={isRunning || !seedText.trim()}
                    className="flex min-h-[44px] items-center justify-center gap-2 rounded-lg bg-primary px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
                >
                    {isRunning ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                    {isRunning ? "生成中" : "生成系列"}
                </button>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
                {EPISODE_OPTIONS.map((count) => (
                    <button
                        key={count}
                        onClick={() => setEpisodeCount(count)}
                        className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${episodeCount === count
                            ? "bg-primary/20 text-white ring-1 ring-primary/40"
                            : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                            }`}
                    >
                        {count} 集
                    </button>
                ))}
                {result ? (
                    <span className="text-xs text-emerald-200">
                        已生成 {packageStats.episodes} 集 · {packageStats.frames} 分镜 · {packageStats.costumes} 服装 · {packageStats.effects} 特效
                    </span>
                ) : null}
            </div>

            {error ? (
                <div className="mt-3 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">
                    <AlertCircle size={16} />
                    {error}
                </div>
            ) : null}
        </section>
    );
}

/**
 * Displays one compact production artifact type in the producer entry header.
 */
function ProcessChip({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
    return (
        <div className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2">
            <div className="flex items-center gap-2 text-gray-400">
                {icon}
                <span>{label}</span>
            </div>
            <div className="mt-1 text-sm font-semibold text-white">{value}</div>
        </div>
    );
}
