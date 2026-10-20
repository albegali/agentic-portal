import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiFetch, captureToken, getToken, hasToken, UnauthorizedError } from "./token";

beforeEach(() => {
  window.sessionStorage.clear();
  window.history.replaceState(null, "", "/");
});
afterEach(() => vi.restoreAllMocks());

describe("captureToken", () => {
  it("stores the fragment token and removes it from the address bar", () => {
    window.history.replaceState(null, "", "/?a=1#token=abc-123");
    captureToken();
    expect(getToken()).toBe("abc-123");
    expect(window.location.hash).toBe("");
    expect(window.location.search).toBe("?a=1");
  });

  it("does nothing without a token fragment", () => {
    window.history.replaceState(null, "", "/#/plan");
    captureToken();
    expect(hasToken()).toBe(false);
    expect(window.location.hash).toBe("#/plan");
  });

  it("never logs the token", () => {
    const spies = (["log", "info", "warn", "error", "debug"] as const).map((m) => vi.spyOn(console, m));
    window.history.replaceState(null, "", "/#token=secret");
    captureToken();
    spies.forEach((s) => expect(s).not.toHaveBeenCalled());
  });

  it("survives blocked storage", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    window.history.replaceState(null, "", "/#token=abc");
    expect(() => captureToken()).not.toThrow();
    expect(window.location.hash).toBe("");
  });
});

describe("apiFetch", () => {
  it("sends the bearer header", async () => {
    window.sessionStorage.setItem("portal.token", "tok");
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 200 }));
    await apiFetch("/api/x", { headers: { Accept: "application/json" } });
    const headers = new Headers((f.mock.calls[0][1] as RequestInit).headers);
    expect(headers.get("Authorization")).toBe("Bearer tok");
    expect(headers.get("Accept")).toBe("application/json");
  });

  it("sends no Authorization header without a token", async () => {
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 200 }));
    await apiFetch("/api/x");
    expect(new Headers((f.mock.calls[0][1] as RequestInit).headers).has("Authorization")).toBe(false);
  });

  it("raises UnauthorizedError on 401", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 401 }));
    await expect(apiFetch("/api/x")).rejects.toBeInstanceOf(UnauthorizedError);
  });
});
