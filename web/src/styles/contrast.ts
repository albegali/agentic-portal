/** WCAG 2.2 contrast maths and the declared token pairs checked by contrast.test.ts. */

export type Rgb = [number, number, number];

export function parseHex(hex: string): Rgb {
  const m = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`not a #rrggbb colour: ${hex}`);
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function blend(top: Rgb, alpha: number, under: Rgb): Rgb {
  return top.map((c, i) => c * alpha + under[i] * (1 - alpha)) as Rgb;
}

function luminance([r, g, b]: Rgb): number {
  const lin = (v: number) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

export function ratio(a: Rgb, b: Rgb): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Backgrounds a foreground can sit on. `glass` is --panel at --glass-pct over the page background. */
export type Surface = "bg" | "panel" | "panel2" | "glass" | "accent";

export type Pair = { fg: string; on: Surface; min: number; use: string };

const TEXT = 4.5; // 1.4.3 normal text
const UI = 3; // 1.4.11 non-text contrast, focus indicator

export const pairs: Pair[] = [
  { fg: "text", on: "bg", min: TEXT, use: "body text" },
  { fg: "text", on: "panel", min: TEXT, use: "text on panels" },
  { fg: "text", on: "panel2", min: TEXT, use: "text on hover/selected rows" },
  { fg: "text", on: "glass", min: TEXT, use: "text on glass panels" },
  { fg: "muted", on: "bg", min: TEXT, use: "secondary text" },
  { fg: "muted", on: "panel", min: TEXT, use: "secondary text on panels" },
  { fg: "muted", on: "panel2", min: TEXT, use: "secondary text on hover/selected rows" },
  { fg: "muted", on: "glass", min: TEXT, use: "secondary text on glass" },
  { fg: "accent-text", on: "bg", min: TEXT, use: "accent text, links" },
  { fg: "accent-text", on: "panel2", min: TEXT, use: "accent text on selected rows" },
  { fg: "accent-text", on: "glass", min: TEXT, use: "accent text on glass" },
  { fg: "onaccent", on: "accent", min: TEXT, use: "text on lime fills" },
  { fg: "focus", on: "bg", min: UI, use: "focus ring on page" },
  { fg: "focus", on: "panel", min: UI, use: "focus ring on panels" },
  { fg: "focus", on: "glass", min: UI, use: "focus ring on glass" },
  ...(["blue", "orange", "green", "red", "yellow"] as const).flatMap((fg) => [
    { fg, on: "bg" as const, min: TEXT, use: `${fg} status text` },
    { fg, on: "glass" as const, min: TEXT, use: `${fg} status text on glass` },
  ]),
];
