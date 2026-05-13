import { describe, expect, it } from "vitest";
import { DEFAULT_STUDIO_THEME, STUDIO_THEMES, resolveStudioTheme } from "@/lib/themePresets";

describe("studio theme presets", () => {
  it("exposes multiple selectable page styles", () => {
    expect(STUDIO_THEMES.length).toBeGreaterThanOrEqual(3);
    expect(STUDIO_THEMES.map((theme) => theme.id)).toContain(DEFAULT_STUDIO_THEME);
  });

  it("falls back to the default theme for invalid persisted values", () => {
    expect(resolveStudioTheme("missing-theme").id).toBe(DEFAULT_STUDIO_THEME);
    expect(resolveStudioTheme(null).id).toBe(DEFAULT_STUDIO_THEME);
  });

  it("keeps canvas colors available for every theme", () => {
    for (const theme of STUDIO_THEMES) {
      expect(theme.background).toMatch(/^#/);
      expect(theme.grid).toMatch(/^#/);
      expect(theme.accent).toMatch(/^#/);
    }
  });
});
