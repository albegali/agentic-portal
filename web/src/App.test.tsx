import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { App } from "./App";

afterEach(() => vi.unstubAllGlobals());

test("shows the portal version from /api/health", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ json: async () => ({ status: "ok", portal_version: "1.2.3" }) }),
  );
  render(<App />);
  expect(await screen.findByText("Portal version 1.2.3")).toBeInTheDocument();
});

test("shows an alert when the server is unreachable", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));
  render(<App />);
  expect(await screen.findByRole("alert")).toBeInTheDocument();
});
