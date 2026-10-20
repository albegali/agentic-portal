// Session token: read once from the launch fragment (#token=…), kept in sessionStorage only,
// sent as a bearer header. Never logged, never put back into a URL.
const KEY = "portal.token";

export const NO_TOKEN_MESSAGE = "Open the portal with `make portal`: this page has no session token.";

export class UnauthorizedError extends Error {
  constructor() {
    super(NO_TOKEN_MESSAGE);
    this.name = "UnauthorizedError";
  }
}

export function getToken(): string | null {
  try {
    return window.sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function hasToken(): boolean {
  return getToken() !== null;
}

/** Call before the router mounts: stores the fragment token and strips the fragment. */
export function captureToken(): void {
  const hash = window.location.hash;
  if (!hash.startsWith("#token=")) return;
  const token = new URLSearchParams(hash.slice(1)).get("token");
  if (token) {
    try {
      window.sessionStorage.setItem(KEY, token);
    } catch {
      // storage blocked: the portal then shows the no-token message
    }
  }
  window.history.replaceState(null, "", window.location.pathname + window.location.search);
}

/** fetch with the bearer header; usable for SSE by reading the response body stream. */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(input, { ...init, headers });
  if (response.status === 401) throw new UnauthorizedError();
  return response;
}
