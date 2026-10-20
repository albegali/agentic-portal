import { useEffect, useState } from "react";
import { apiFetch, hasToken, NO_TOKEN_MESSAGE } from "../../api/token";

type Health = { status: string; portal_version?: string };

export function ServerStatus() {
  const [health, setHealth] = useState<Health | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    apiFetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setFailed(true));
  }, []);

  return (
    <div className="server-status">
      {!hasToken() && <p role="alert">{NO_TOKEN_MESSAGE}</p>}
      {failed && <p role="alert">Server unreachable.</p>}
      {health && <p>Portal version {health.portal_version ?? "unknown"}</p>}
    </div>
  );
}
