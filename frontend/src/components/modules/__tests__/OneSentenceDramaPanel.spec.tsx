import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import OneSentenceDramaPanel from "../OneSentenceDramaPanel";

const mocks = vi.hoisted(() => ({
  runAutoDrama: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    runAutoDrama: mocks.runAutoDrama,
  },
}));

afterEach(() => {
  vi.clearAllMocks();
  window.location.hash = "";
});

describe("OneSentenceDramaPanel", () => {
  it("runs Auto Drama in series persistence mode", async () => {
    const onCreated = vi.fn();
    mocks.runAutoDrama.mockResolvedValue({
      status: "completed",
      title: "夜半信号",
      next_hash: "#/series/series-1",
      episode_packages: [
        { storyboard_frames: [{ id: "f1" }], costumes: [{}], special_effects: [{}] },
        { storyboard_frames: [{ id: "f2" }], costumes: [{}], special_effects: [{}] },
      ],
      series: { id: "series-1" },
      episodes: [{ id: "ep-1" }, { id: "ep-2" }],
    });

    render(<OneSentenceDramaPanel onCreated={onCreated} />);

    fireEvent.click(screen.getByText("生成系列"));

    await waitFor(() => {
      expect(mocks.runAutoDrama).toHaveBeenCalledWith(expect.objectContaining({
        target_chapters: 5,
        persist_project: true,
        persist_mode: "series",
        backend: "dry_run",
      }));
      expect(onCreated).toHaveBeenCalled();
      expect(window.location.hash).toBe("#/series/series-1");
    });
  });
});
