import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { blend, pairs, parseHex, ratio, type Rgb, type Surface } from "./contrast";

const tokensCss = readFileSync("src/styles/tokens.css", "utf8");

type Theme = "light" | "dark";

function readTokens(theme: Theme): Record<string, string> {
  const out: Record<string, string> = {};
  const pair = /--([a-z0-9-]+):\s*light-dark\(\s*(#[0-9a-f]{6})\s*,\s*(#[0-9a-f]{6})\s*\)/gi;
  for (const [, name, light, dark] of tokensCss.matchAll(pair)) out[name] = theme === "light" ? light : dark;
  const plain = /--([a-z0-9-]+):\s*(#[0-9a-f]{6})\s*;/gi;
  for (const [, name, hex] of tokensCss.matchAll(plain)) out[name] ??= hex;
  return out;
}

const glassAlpha = Number(/--glass-pct:\s*(\d+)%/.exec(tokensCss)![1]) / 100;

/** Worst-case page backgrounds: --bg, plus the accent (10%) and blue (9%) radial glows of the body gradient. */
function backdrops(t: Record<string, string>): Rgb[] {
  const bg = parseHex(t.bg);
  const withAccent = blend(parseHex(t.accent), 0.1, bg);
  const withBlue = blend(parseHex(t.blue), 0.09, bg);
  return [bg, withAccent, withBlue, blend(parseHex(t.blue), 0.09, withAccent)];
}

function surfaces(t: Record<string, string>, on: Surface): Rgb[] {
  if (on === "glass") return backdrops(t).map((b) => blend(parseHex(t.panel), glassAlpha, b));
  if (on === "bg") return backdrops(t);
  return [parseHex(t[on])];
}

for (const theme of ["light", "dark"] as const) {
  const tokens = readTokens(theme);
  test.each(pairs)(`$theme: $fg on $on ($use) >= $min`.replace("$theme", theme), ({ fg, on, min }) => {
    expect(tokens[fg], `token --${fg} declared`).toBeDefined();
    const worst = Math.min(...surfaces(tokens, on).map((s) => ratio(parseHex(tokens[fg]), s)));
    expect(worst).toBeGreaterThanOrEqual(min);
  });
}

test("tokens.css declares a light and a dark value for every themed colour", () => {
  const themed = [...tokensCss.matchAll(/--([a-z0-9-]+):\s*light-dark\(/gi)].map((m) => m[1]);
  expect(themed.length).toBeGreaterThan(10);
});
