import { beforeEach, describe, expect, it, vi } from "vitest";
import axios from "axios";
import { api, API_URL } from "@/lib/api";

vi.mock("axios", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe("workflow switch API client", () => {
  beforeEach(() => {
    vi.mocked(axios.get).mockReset();
  });

  it("loads workflow_switch modules for the QA visible panel", async () => {
    vi.mocked(axios.get).mockResolvedValue({
      data: {
        status: "ready",
        source: "docs/Codex_Workflow_Prompts",
        modules: [
          {
            order: 0,
            title: "Global Rules",
            path: "docs/Codex_Workflow_Prompts/00_GLOBAL_RULES.md",
            switch: {
              module_id: "00_global_rules",
              stage_id: "global_rules",
              label: "Global Rules",
              auto_advance: true,
              requires_human_review: false,
              stop_after_stage: false,
            },
          },
        ],
        execution_plan: { status: "ready", summary: { module_count: 1, auto_modules: 1 } },
      },
    });

    const result = await api.getWorkflowPromptSwitches();

    expect(axios.get).toHaveBeenCalledWith(`${API_URL}/film/workflow/prompts`);
    expect(result.modules[0].switch.auto_advance).toBe(true);
  });
});
