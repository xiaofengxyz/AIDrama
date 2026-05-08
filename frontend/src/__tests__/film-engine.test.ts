import { describe, expect, it } from "vitest";
import {
  buildFilmPipelinePayload,
  buildFilmSourceText,
  evaluateFilmEngineStages,
  getFilmEngineMetrics,
} from "@/lib/filmEngine";

describe("buildFilmPipelinePayload", () => {
  it("maps project script and locked assets into Film Core payload", () => {
    const payload = buildFilmPipelinePayload({
      id: "project-1",
      title: "Proof",
      originalText: "INT. SAFE HOUSE\nMaya: Hide it. [prop=evidence_phone]",
      characters: [
        {
          id: "maya",
          name: "Maya",
          description: "brave analyst",
          clothing: "blue raincoat",
          locked: true,
          image_url: "refs/maya.png",
        },
      ],
      scenes: [
        {
          id: "safe_house",
          name: "Safe House",
          description: "hidden room",
          lighting_mood: "cold fluorescent",
        },
      ],
      props: [
        {
          id: "evidence_phone",
          name: "Evidence Phone",
          description: "cracked screen",
          locked: true,
          image_url: "refs/phone.png",
        },
      ],
      frames: [],
      status: "draft",
      createdAt: "",
      updatedAt: "",
    } as any);

    expect(payload.script_text).toContain("[prop=evidence_phone]");
    expect(payload.backend).toBe("dry_run");
    expect((payload.characters?.[0] as any).reference_images).toEqual(["refs/maya.png"]);
    expect((payload.characters?.[0] as any).locked_traits).toContain("identity_locked");
    expect((payload.props?.[0] as any).locked_traits).toContain("prop_locked");
    expect((payload.continuity_locks?.characters as any).maya.locked_traits).toContain("identity_locked");
  });

  it("builds a deterministic script from storyboard frames when raw script is empty", () => {
    const script = buildFilmSourceText({
      id: "project-2",
      title: "Frame Story",
      originalText: "",
      characters: [{ id: "hero", name: "Hero" }],
      scenes: [{ id: "street", name: "Night Street", description: "" }],
      props: [],
      frames: [
        {
          id: "frame-1",
          scene_id: "street",
          character_ids: ["hero"],
          dialogue: "We move now.",
          action_description: "Hero checks the alley",
          prop_ids: ["phone"],
        },
      ],
      status: "draft",
      createdAt: "",
      updatedAt: "",
    } as any);

    expect(script).toContain("INT. NIGHT STREET");
    expect(script).toContain("Hero: We move now.");
    expect(script).toContain("[prop=phone]");
  });
});

describe("evaluateFilmEngineStages", () => {
  const response = {
    story_graph: { graph_id: "film_project", beats: [{}], metadata: { builder_version: "story_graph.v1" } },
    director_program: {
      sequence_id: "film_project",
      shots: [{ id: "shot_001" }],
      metadata: { planner_version: "director_planner.v1" },
    },
    film_run: {
      summary: {
        total_shots: 1,
        accepted_shots: 1,
        failed_shots: 0,
        total_attempts: 1,
        retry_attempts: 0,
        average_qa_score: 1,
        total_cost_estimate: 0,
      },
      shot_graph: { sequence_id: "film_project", shots: [{ id: "shot_001" }], transitions: [] },
      final_state: {
        character_states: { maya: {} },
        scene_states: { safe_house: {} },
        timeline: [{ shot_id: "shot_001" }],
      },
      qa_reports: [{ shot_id: "shot_001", score: 1, threshold: 0.82, findings: [] }],
    },
    generation_ledger: {
      shot_runs: {
        shot_001: {
          shot_id: "shot_001",
          status: "accepted",
          selected_output_uri: "dry-run://shot_001",
          attempts: [{ prompt: "prompt", prompt_fingerprint: "abc" }],
        },
      },
    },
    final_edit: {
      clips: [{ clip_id: "clip_001", duration: 4 }],
      total_duration: 4,
      unresolved_shots: [],
      qa_summary: { average_qa_score: 1, unresolved_count: 0 },
    },
    metadata: { backend: "dry_run", pipeline_version: "film_production_pipeline.v1" },
  } as any;

  it("shows all nine fixed Film Engine stages before a run", () => {
    const stages = evaluateFilmEngineStages(null);
    expect(stages).toHaveLength(9);
    expect(stages.map((stage) => stage.order)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    expect(stages.every((stage) => stage.status === "implemented")).toBe(true);
  });

  it("marks a successful dry-run across all nine stages", () => {
    const stages = evaluateFilmEngineStages(response);
    expect(stages).toHaveLength(9);
    expect(stages.every((stage) => stage.status === "passed")).toBe(true);
  });

  it("summarizes production metrics for the control room", () => {
    expect(getFilmEngineMetrics(response)).toMatchObject({
      beats: 1,
      shots: 1,
      acceptedShots: 1,
      failedShots: 0,
      totalAttempts: 1,
      retryAttempts: 0,
      qaScore: 1,
      unresolvedShots: 0,
      totalDuration: 4,
    });
  });
});
