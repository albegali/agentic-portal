# Accessibility checklist (per release)

Manual checks that complement the automated ones (`npm --prefix web test` contrast test, `npm --prefix web run e2e` axe over every registered route, both themes, Chromium + WebKit + Firefox). Target: WCAG 2.2 AA (NFR-11). Run once per release candidate, on the built bundle (`make run`), and record the result in the table at the bottom.

| # | Check | How |
|---|---|---|
| 1 | Tab order | From a fresh load press Tab: skip link first, then the navigation in visual order, then the content. No keyboard trap; focus never lands on hidden content. On Safari/macOS use Option+Tab. |
| 2 | Focus visible | Every focused control shows a clear ring in light and dark. |
| 3 | Skip link | Enter on the skip link moves focus to the main content; the URL route does not change. |
| 4 | Landmarks | A screen reader or the browser accessibility tree lists one navigation ("Main") and one main region; headings start at one h1 per screen. |
| 5 | Drawer (below 900 px) | Menu button opens the drawer and focuses the current page; Escape and a tap outside close it and focus returns to the button; content behind is not reachable while open. |
| 6 | Reflow 200% | Browser zoom 200% at 1280 px wide: nothing is cut off, no two-dimensional scrolling. |
| 7 | Reflow 400% | Zoom 400% (equivalent to 320 px): no horizontal scroll, navigation usable. |
| 8 | 375 px | Device mode 375 px: no horizontal scroll, touch targets at least 44 px. |
| 9 | Reduced motion | Enable "reduce motion" in the OS: no transitions or animations remain. |
| 10 | Both themes | Switch the OS between light and dark: text, focus and status colours stay legible; no hard-to-read glass areas. |
| 11 | Screen reader smoke test | VoiceOver (macOS) or NVDA (Windows): navigate by landmarks and headings, open every section from the navigation, hear the page title and current page announced. |
| 12 | Text only from the bundle | Offline (network off, localhost only): text still renders in Quicksand. |

New screens add their own rows here when they introduce controls the list does not cover (dialogs, tabs, tables, diagrams).

## Results

| Release | Date | Tester | Browser / screen reader | Result | Notes |
|---|---|---|---|---|---|
| | | | | | |
