import { describe, expect, it } from "vitest";
import {
  buildProjectWorkbenchHash,
  buildSeriesEpisodeWorkbenchHash,
  parseWorkspaceHash,
} from "@/lib/workspaceRouting";

describe("workspace routing", () => {
  it("parses standalone project workbench hashes with optional step deep links", () => {
    expect(parseWorkspaceHash("#/project/project-1")).toEqual({
      view: "project",
      projectId: "project-1",
      stepId: undefined,
    });
    expect(parseWorkspaceHash("#/project/project-1/step/export")).toEqual({
      view: "project",
      projectId: "project-1",
      stepId: "export",
    });
  });

  it("parses series episode workbench hashes with a QA & Export alias", () => {
    expect(parseWorkspaceHash("#/series/series-1/episode/ep-1/step/QA%20%26%20Export")).toEqual({
      view: "series-episode",
      seriesId: "series-1",
      episodeId: "ep-1",
      stepId: "export",
    });
  });

  it("builds stable hashes for QA & Export entry points", () => {
    expect(buildProjectWorkbenchHash("project 1", "export")).toBe("#/project/project%201/step/export");
    expect(buildSeriesEpisodeWorkbenchHash("series 1", "ep 1", "export")).toBe(
      "#/series/series%201/episode/ep%201/step/export"
    );
  });
});
