import { useEffect, useState } from "react";

type Health = { status: string; portal_version?: string };

export function ServerStatus() {
  const [health, setHealth] = useState<Health | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setFailed(true));
  }, []);

  return (
    <div className="server-status">
      {failed && <p role="alert">Server unreachable.</p>}
      {health && <p>Portal version {health.portal_version ?? "unknown"}</p>}
    </div>
  );
}
