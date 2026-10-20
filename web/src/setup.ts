import "@testing-library/jest-dom/vitest";

// jsdom has no matchMedia; the shell only listens to it while the drawer is open.
if (!window.matchMedia) {
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    addEventListener: () => {},
    removeEventListener: () => {},
  })) as unknown as typeof window.matchMedia;
}
