import { expect, test } from "@playwright/test";
import { routes } from "../src/routes";

test.use({ viewport: { width: 375, height: 800 } });

for (const route of routes) {
  test(`375 px: no horizontal scroll on ${route.label}`, async ({ page }) => {
    await page.goto(`/#${route.path}`);
    await expect(page.getByRole("heading", { level: 1, name: route.label })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
}

test("375 px: menu button and navigation targets are at least 44 px", async ({ page }) => {
  await page.goto("/#/");
  const menu = await page.getByRole("button", { name: "Menu" }).boundingBox();
  expect(menu!.height).toBeGreaterThanOrEqual(44);
  expect(menu!.width).toBeGreaterThanOrEqual(44);
  await page.getByRole("button", { name: "Menu" }).click();
  for (const route of routes) {
    const box = await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: route.label, exact: true }).boundingBox();
    expect(box!.height, route.label).toBeGreaterThanOrEqual(44);
  }
});

test("reduced motion: the drawer does not animate", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/#/");
  const duration = await page.getByRole("navigation", { name: "Main", includeHidden: true }).evaluate((el) => getComputedStyle(el).transitionDuration);
  expect(duration.split(",").every((d) => parseFloat(d) === 0)).toBe(true);
});
