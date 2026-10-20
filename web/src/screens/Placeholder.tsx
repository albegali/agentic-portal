import type { AppRoute } from "../routes";

export function Placeholder({ route }: { route: AppRoute }) {
  return (
    <>
      <h1>{route.label}</h1>
      <p className="muted">{route.summary}</p>
      <p>This screen is not implemented yet.</p>
    </>
  );
}
