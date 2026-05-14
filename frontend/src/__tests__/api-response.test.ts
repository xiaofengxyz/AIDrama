import { describe, expect, it } from "vitest";
import { ensureArrayResponse, resolveApiUrl } from "@/lib/api";

describe("resolveApiUrl", () => {
  it("uses the explicit runtime API URL when provided", () => {
    expect(resolveApiUrl({ configuredUrl: "http://localhost:48217/" }))
      .toBe("http://localhost:48217");
  });

  it("routes the uncommon frontend dev port to the uncommon backend port", () => {
    expect(resolveApiUrl({ protocol: "http:", hostname: "localhost", port: "39211" }))
      .toBe("http://localhost:48217");
  });

  it("keeps same-origin URLs for packaged backend-served pages", () => {
    expect(resolveApiUrl({ protocol: "http:", hostname: "localhost", port: "48217" }))
      .toBe("http://localhost:48217");
  });
});

describe("ensureArrayResponse", () => {
  it("returns array payloads unchanged", () => {
    const payload = [{ id: "series-1" }];
    expect(ensureArrayResponse(payload, "GET /series")).toBe(payload);
  });

  it("throws a clear routing error when nginx returns frontend HTML", () => {
    expect(() => ensureArrayResponse("<!DOCTYPE html><html></html>", "GET /series"))
      .toThrow(/GET \/series expected a JSON array but received HTML document/);
  });

  it("throws a clear schema error for object payloads", () => {
    expect(() => ensureArrayResponse({ detail: "Method Not Allowed" }, "GET /projects/"))
      .toThrow(/GET \/projects\/ expected a JSON array but received object/);
  });
});
