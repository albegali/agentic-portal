import { expect, test } from "@playwright/test";

test("text uses the bundled Quicksand and nothing leaves localhost", async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const external: string[] = [];
  page.on("request", (req) => {
    const url = req.url();
    if (!url.startsWith(origin) && !url.startsWith("data:") && !url.startsWith("blob:")) external.push(url);
  });
  await page.goto("/#/");
  await page.waitForLoadState("networkidle");
  await page.evaluate(() => document.fonts.ready);
  const result = await page.evaluate(() => ({
    family: getComputedStyle(document.body).fontFamily,
    loaded: [...document.fonts].some((f) => f.family.includes("Quicksand") && f.status === "loaded"),
  }));
  expect(result.family).toContain("Quicksand Variable");
  expect(result.loaded).toBe(true);
  expect(external).toEqual([]);
});
