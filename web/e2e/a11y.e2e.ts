import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { routes } from "../src/routes";

// WCAG 2.0 / 2.1 / 2.2, levels A and AA.
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

for (const colorScheme of ["light", "dark"] as const) {
  for (const route of routes) {
    test(`axe: ${route.label} (${colorScheme})`, async ({ page }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(`/#${route.path}`);
      await expect(page.getByRole("heading", { level: 1, name: route.label })).toBeVisible();
      const { violations } = await new AxeBuilder({ page }).withTags(TAGS).analyze();
      expect(violations, JSON.stringify(violations.map((v) => [v.id, v.nodes.map((n) => n.target)]))).toEqual([]);
    });
  }

  test(`axe: open drawer at 375 px (${colorScheme})`, async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.emulateMedia({ colorScheme });
    await page.goto("/#/");
    await page.getByRole("button", { name: "Menu" }).click();
    await expect(page.getByRole("navigation", { name: "Main" })).toBeVisible();
    const { violations } = await new AxeBuilder({ page }).withTags(TAGS).analyze();
    expect(violations, JSON.stringify(violations.map((v) => [v.id, v.nodes.map((n) => n.target)]))).toEqual([]);
  });
}
