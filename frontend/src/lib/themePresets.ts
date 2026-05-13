export type StudioThemeId = "studio-noir" | "dailies-green" | "ember-cut";

export interface StudioThemePreset {
    /** Stable id persisted to localStorage and mirrored on the html data attribute. */
    id: StudioThemeId;
    /** Short label displayed in the compact theme switcher. */
    label: string;
    /** Canvas background color used by the Three.js scene. */
    background: string;
    /** Grid line color used by the background canvas. */
    grid: string;
    /** Secondary accent color used by the background canvas. */
    accent: string;
}

/**
 * Curated page themes for long-running Studio work sessions.
 */
export const STUDIO_THEMES: StudioThemePreset[] = [
    {
        id: "studio-noir",
        label: "Noir",
        background: "#050508",
        grid: "#68e1fd",
        accent: "#f6c177",
    },
    {
        id: "dailies-green",
        label: "Dailies",
        background: "#07110d",
        grid: "#8bd7a3",
        accent: "#f5d06f",
    },
    {
        id: "ember-cut",
        label: "Ember",
        background: "#13080a",
        grid: "#ff7a59",
        accent: "#7dd3fc",
    },
];

/** Default Studio theme used when no valid preference has been saved. */
export const DEFAULT_STUDIO_THEME: StudioThemeId = "studio-noir";

/**
 * Resolve persisted or user-supplied theme ids without leaking invalid values to the DOM.
 */
export function resolveStudioTheme(themeId?: string | null): StudioThemePreset {
    return STUDIO_THEMES.find((theme) => theme.id === themeId) || STUDIO_THEMES[0];
}
