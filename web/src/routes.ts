/** Route registry: the single list of sections. The shell, the router and the e2e axe suite all read it. */
export type AppRoute = { path: string; label: string; summary: string };

export const routes: AppRoute[] = [
  { path: "/", label: "Overview", summary: "Next step, what is waiting for you, sprint and project health." },
  { path: "/plan", label: "Plan", summary: "Releases and sprints." },
  { path: "/backlog", label: "Backlog", summary: "Epics and stories, board or list." },
  { path: "/approvals", label: "Approvals", summary: "Human gates waiting for a decision." },
  { path: "/runs", label: "Agent runs", summary: "History and live output of agent runs." },
  { path: "/insights", label: "Insights", summary: "Weak files, security findings and untested code." },
  { path: "/architecture", label: "Architecture", summary: "Component and infrastructure diagrams." },
  { path: "/journal", label: "Journal", summary: "Weekly and monthly project journal." },
  { path: "/settings", label: "Settings", summary: "Skeleton contract, agent CLI, tiers and project." },
];

export const APP_NAME = "Agentic Portal";
