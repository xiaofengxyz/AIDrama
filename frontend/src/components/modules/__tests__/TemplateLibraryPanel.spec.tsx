import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import TemplateLibraryPanel from "../TemplateLibraryPanel";
import type { FilmTemplateCatalog } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  getFilmTemplates: vi.fn(),
  createProjectFromPilotTemplate: vi.fn(),
  createSeriesFromTemplate: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    getFilmTemplates: mocks.getFilmTemplates,
    createProjectFromPilotTemplate: mocks.createProjectFromPilotTemplate,
    createSeriesFromTemplate: mocks.createSeriesFromTemplate,
  },
}));

const catalog = {
  status: "ready",
  source: "repository_samples",
  pilot_samples: {
    id: "three_vertical_pilot_samples",
    purpose: "validate directions",
    samples: [
      {
        sample_id: "suspense_signal_75s",
        title: "Night Signal",
        genre: "urban_suspense",
        target_duration_seconds: 75,
        audience_hook: "a cracked phone keeps calling",
        production_risk: "one face and one phone must stay consistent",
        success_metric: "first three seconds retention",
        script_text: "INT. NIGHT CORRIDOR\nMaya: The phone is calling.",
      },
      {
        sample_id: "contract_bride_80s",
        title: "Contract Bride Counterattack",
        genre: "romance_revenge",
        target_duration_seconds: 80,
        audience_hook: "a fake bride exposes hidden debt",
        production_risk: "dialogue closeup continuity",
        success_metric: "completion rate",
        script_text: "INT. HOTEL SUITE\nLina signs.",
      },
      {
        sample_id: "midnight_delivery_70s",
        title: "Midnight Delivery",
        genre: "urban_fantasy_case",
        target_duration_seconds: 70,
        audience_hook: "a courier reaches a vanished address",
        production_risk: "scene continuity",
        success_metric: "shares",
        script_text: "EXT. RAINY ALLEY\nJun checks the app.",
      },
    ],
  },
  series_blueprints: [
    {
      id: "night_signal_s01",
      title: "Night Signal Season 1",
      backend: "dry_run",
      characters: [{}],
      scenes: [{}, {}, {}, {}, {}],
      props: [{}, {}],
      costumes: [{}, {}],
      episodes: [
        { episode_id: "ep01", title: "One", script_text: "INT. ROOM\nOne" },
        { episode_id: "ep02", title: "Two", script_text: "INT. ROOM\nTwo" },
        { episode_id: "ep03", title: "Three", script_text: "INT. ROOM\nThree" },
        { episode_id: "ep04", title: "Four", script_text: "INT. ROOM\nFour" },
        { episode_id: "ep05", title: "Five", script_text: "INT. ROOM\nFive" },
      ],
      metadata: {
        format: "vertical_9_16",
        target_episode_duration_seconds: 75,
      },
    },
  ],
  summary: {
    pilot_sample_count: 3,
    series_blueprint_count: 1,
    episode_count: 5,
  },
} satisfies FilmTemplateCatalog;

afterEach(() => {
  vi.clearAllMocks();
  window.location.hash = "";
});

describe("TemplateLibraryPanel", () => {
  it("renders pilot and five-episode series templates from the backend catalog", async () => {
    mocks.getFilmTemplates.mockResolvedValue(catalog);

    render(<TemplateLibraryPanel />);

    expect(await screen.findByText("AI 漫剧模板中心")).toBeInTheDocument();
    expect(screen.getByText("3 个样片 · 5 集验证")).toBeInTheDocument();
    expect(screen.getByText("Night Signal")).toBeInTheDocument();
    expect(screen.getByText("Night Signal Season 1")).toBeInTheDocument();
    expect(screen.getByText("创建 5 集系列")).toBeInTheDocument();
  });

  it("creates a pilot project and opens the returned QA route", async () => {
    const onCreated = vi.fn();
    mocks.getFilmTemplates.mockResolvedValue(catalog);
    mocks.createProjectFromPilotTemplate.mockResolvedValue({
      created_type: "pilot_project",
      template_id: "midnight_delivery_70s",
      next_hash: "#/project/project-1/step/export",
      project: { id: "project-1" },
      episodes: [],
    });

    render(<TemplateLibraryPanel onCreated={onCreated} />);

    await screen.findByText("Midnight Delivery");
    fireEvent.click(screen.getAllByText("创建样片")[0]);

    await waitFor(() => {
      expect(mocks.createProjectFromPilotTemplate).toHaveBeenCalledWith("midnight_delivery_70s");
      expect(onCreated).toHaveBeenCalled();
      expect(window.location.hash).toBe("#/project/project-1/step/export");
    });
  });
});
