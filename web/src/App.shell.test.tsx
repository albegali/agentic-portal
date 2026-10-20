import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { App } from "./App";
import { APP_NAME, routes } from "./routes";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ json: async () => ({ status: "ok", portal_version: "1.0.0" }) }));
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.location.hash = "";
});

describe("route registry", () => {
  test("has unique paths and labels, starting with the overview", () => {
    expect(new Set(routes.map((r) => r.path)).size).toBe(routes.length);
    expect(new Set(routes.map((r) => r.label)).size).toBe(routes.length);
    expect(routes[0].path).toBe("/");
  });

  test.each(routes)("$label renders a level-1 heading and sets the document title", ({ path, label }) => {
    window.location.hash = `#${path}`;
    render(<App />);
    expect(screen.getByRole("heading", { level: 1, name: label })).toBeInTheDocument();
    expect(document.title).toBe(`${label} — ${APP_NAME}`);
    expect(screen.getByRole("link", { name: label })).toHaveAttribute("aria-current", "page");
  });
});

describe("shell", () => {
  test("exposes banner-free landmarks: one navigation, one main, and a skip link first in tab order", async () => {
    render(<App />);
    expect(screen.getByRole("navigation", { name: "Main" })).toBeInTheDocument();
    expect(screen.getAllByRole("main")).toHaveLength(1);
    await userEvent.tab();
    expect(screen.getByRole("link", { name: "Skip to content" })).toHaveFocus();
  });

  test("skip link focuses main and leaves the route hash untouched", async () => {
    window.location.hash = "#/plan";
    render(<App />);
    await userEvent.click(screen.getByRole("link", { name: "Skip to content" }));
    expect(screen.getByRole("main")).toHaveFocus();
    expect(window.location.hash).toBe("#/plan");
  });

  test("navigation is reachable by keyboard and moves focus to the content", async () => {
    render(<App />);
    const plan = screen.getByRole("link", { name: "Plan" });
    plan.focus();
    await userEvent.keyboard("{Enter}");
    expect(screen.getByRole("heading", { level: 1, name: "Plan" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveFocus();
  });

  test("drawer: opens from the menu button, closes on Escape and returns focus", async () => {
    render(<App />);
    const menu = screen.getByRole("button", { name: "Menu" });
    expect(menu).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(menu);
    expect(menu).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("main")).toHaveAttribute("inert");
    await userEvent.keyboard("{Escape}");
    expect(menu).toHaveAttribute("aria-expanded", "false");
    expect(menu).toHaveFocus();
    expect(screen.getByRole("main")).not.toHaveAttribute("inert");
  });

  test("drawer closes when the current page's link is chosen", async () => {
    render(<App />);
    const menu = screen.getByRole("button", { name: "Menu" });
    await userEvent.click(menu);
    await userEvent.click(screen.getByRole("link", { name: "Overview" }));
    expect(menu).toHaveAttribute("aria-expanded", "false");
  });
});
