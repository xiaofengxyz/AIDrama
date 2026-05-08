import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(testDir, "../../..");
const nginxConf = readFileSync(path.join(repoRoot, "docker/nginx.conf"), "utf8");

describe("docker nginx API proxy config", () => {
  it("proxies every frontend API prefix that is used from the browser", () => {
    const requiredPrefixes = [
      "/projects",
      "/series",
      "/files/",
      "/tasks/",
      "/art_direction/",
      "/upload",
      "/video/",
      "/voices",
      "/config/",
      "/film/",
    ];

    for (const prefix of requiredPrefixes) {
      const escapedPrefix = prefix.replace(/\//g, "\\/");
      expect(nginxConf).toMatch(new RegExp(`location\\s+${escapedPrefix}(?:\\s|\\{)`));
    }
  });
});
