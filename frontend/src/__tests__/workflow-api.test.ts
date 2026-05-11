import { afterEach, describe, expect, it, vi } from "vitest";
import { api, API_URL } from "@/lib/api";

function jsonResponse(payload: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("workflow API client", () => {
  it("returns render package export responses instead of assuming every export is mp4", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({
      url: "export/project_render_package.json",
      mode: "render_package",
      warnings: ["No final mp4 was created because selected video clips are not complete."],
      action_required: ["Generate and select video clips for each frame."],
      workflow_state: {
        project_id: "project-1",
        title: "Project",
        version: "cineforge_workflow.v1",
        stages: [],
        summary: { recommended_render_mode: "render_package" },
      },
    }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await api.exportProject("project-1", { allow_package_fallback: true });

    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/projects/project-1/export`, expect.objectContaining({
      method: "POST",
    }));
    expect(result.mode).toBe("render_package");
    expect(result.workflow_state?.summary.recommended_render_mode).toBe("render_package");
  });

  it("surfaces backend export details instead of a generic failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({
      detail: "No videos selected to merge. Please select videos for each frame first.",
    }, false, 400)));

    await expect(api.exportProject("project-1", {})).rejects.toThrow(/No videos selected/);
  });

  it("loads persisted workflow state for the QA control room", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({
      project_id: "project-1",
      title: "Project",
      version: "cineforge_workflow.v1",
      stages: [{ id: "video_runtime", status: "attention" }],
      summary: { selected_video_frames: 0 },
    })));

    const state = await api.getProjectWorkflow("project-1");

    expect(state.version).toBe("cineforge_workflow.v1");
    expect(state.stages[0].id).toBe("video_runtime");
  });
});
