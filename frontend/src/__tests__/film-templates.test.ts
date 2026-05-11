import { describe, expect, it } from "vitest";
import type { FilmTemplateCatalog } from "@/lib/api";
import {
  getSeriesTemplateStats,
  getTemplateCatalogStats,
  hasRequiredDramaTemplates,
  sortPilotTemplates,
} from "@/lib/filmTemplates";

const catalog = {
  status: "ready",
  source: "repository_samples",
  pilot_samples: {
    id: "three_vertical_pilot_samples",
    purpose: "validate directions",
    samples: [
      {
        sample_id: "sample_b",
        title: "B",
        genre: "suspense",
        target_duration_seconds: 80,
        audience_hook: "hook",
        production_risk: "risk",
        success_metric: "metric",
        script_text: "INT. ROOM\nB",
      },
      {
        sample_id: "sample_a",
        title: "A",
        genre: "romance",
        target_duration_seconds: 70,
        audience_hook: "hook",
        production_risk: "risk",
        success_metric: "metric",
        script_text: "INT. ROOM\nA",
      },
      {
        sample_id: "sample_c",
        title: "C",
        genre: "fantasy",
        target_duration_seconds: 75,
        audience_hook: "hook",
        production_risk: "risk",
        success_metric: "metric",
        script_text: "INT. ROOM\nC",
      },
    ],
  },
  series_blueprints: [
    {
      id: "night_signal_s01",
      title: "Night Signal",
      backend: "dry_run",
      characters: [{}],
      scenes: [{}, {}, {}],
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

describe("film template helpers", () => {
  it("summarizes required pilot and series template coverage", () => {
    expect(getTemplateCatalogStats(catalog)).toEqual({
      pilotSampleCount: 3,
      seriesBlueprintCount: 1,
      totalEpisodeCount: 5,
    });
    expect(hasRequiredDramaTemplates(catalog)).toBe(true);
  });

  it("sorts pilot templates by duration for stable rendering", () => {
    expect(sortPilotTemplates(catalog.pilot_samples.samples).map((sample) => sample.sample_id))
      .toEqual(["sample_a", "sample_c", "sample_b"]);
  });

  it("extracts continuity asset stats from the five-episode blueprint", () => {
    expect(getSeriesTemplateStats(catalog.series_blueprints[0])).toMatchObject({
      episodeCount: 5,
      characterCount: 1,
      sceneCount: 3,
      propCount: 2,
      costumeCount: 2,
      targetDurationSeconds: 75,
      format: "vertical_9_16",
    });
  });
});
