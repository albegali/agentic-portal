import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ServerStatus } from "./ServerStatus";
import { NO_TOKEN_MESSAGE } from "../../api/token";

beforeEach(() => {
  window.sessionStorage.clear();
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ status: "ok", portal_version: "1" })));
});
afterEach(() => vi.restoreAllMocks());

it("explains how to open the portal when there is no token", async () => {
  render(<ServerStatus />);
  expect(screen.getByRole("alert")).toHaveTextContent(NO_TOKEN_MESSAGE);
  expect(await screen.findByText(/Portal version 1/)).toBeInTheDocument();
});

it("shows no token message when a token is stored", async () => {
  window.sessionStorage.setItem("portal.token", "t");
  render(<ServerStatus />);
  expect(await screen.findByText(/Portal version 1/)).toBeInTheDocument();
  expect(screen.queryByText(NO_TOKEN_MESSAGE)).toBeNull();
});
