import { expect, test } from "@playwright/test";
import { routes } from "../src/routes";

// Safari on macOS skips links on Tab unless Option is held; other engines tab to links.
const tabKey = (browserName: string) => (browserName === "webkit" && process.platform === "darwin" ? "Alt+Tab" : "Tab");

test("desktop: skip link first, then every section in order, each with a visible focus ring", async ({ page, browserName }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/#/");
  await page.keyboard.press(tabKey(browserName));
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  await page.keyboard.press(tabKey(browserName));
  for (const route of routes) {
    const link = page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: route.label, exact: true });
    await expect(link).toBeFocused();
    const outline = await link.evaluate((el) => getComputedStyle(el).outlineWidth);
    expect(parseFloat(outline)).toBeGreaterThanOrEqual(2);
    await page.keyboard.press(tabKey(browserName));
  }
});

test("skip link moves focus to the content and keeps the route", async ({ page, browserName }) => {
  await page.goto("/#/plan");
  await page.keyboard.press(tabKey(browserName));
  await page.keyboard.press("Enter");
  await expect(page.getByRole("main")).toBeFocused();
  expect(page.url()).toContain("/#/plan");
});

test("selecting a section by keyboard shows it and focuses the content", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/#/");
  await page.getByRole("link", { name: "Backlog", exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { level: 1, name: "Backlog" })).toBeVisible();
  await expect(page.getByRole("main")).toBeFocused();
});

test("mobile drawer: closed links are unreachable, Escape closes and returns focus", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto("/#/plan");
  const nav = page.getByRole("navigation", { name: "Main" });
  const menu = page.getByRole("button", { name: "Menu" });
  await expect(nav).toBeHidden();
  await menu.focus();
  await page.keyboard.press("Enter");
  await expect(nav).toBeVisible();
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(nav.getByRole("link", { name: "Plan", exact: true })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(nav).toBeHidden();
  await expect(menu).toBeFocused();
});

test("mobile drawer closes on tap outside", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto("/#/");
  await page.getByRole("button", { name: "Menu" }).click();
  await page.mouse.click(360, 400);
  await expect(page.getByRole("navigation", { name: "Main" })).toBeHidden();
});
