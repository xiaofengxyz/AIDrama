import { describe, expect, it } from "vitest";
import { ensureArrayResponse } from "@/lib/api";

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
