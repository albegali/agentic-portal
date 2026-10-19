import { useEffect, useState } from "react";

type Health = { status: string; portal_version?: string };

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setFailed(true));
  }, []);

  return (
    <main>
      <h1>Agentic Portal</h1>
      {failed && <p role="alert">Server unreachable.</p>}
      {health && <p>Portal version {health.portal_version ?? "unknown"}</p>}
    </main>
  );
}
