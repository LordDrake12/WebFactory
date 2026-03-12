import type { AuthResponse, WorldSnapshot, WorldSummary } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return (await res.json()) as T;
}

export const api = {
  register: (username: string, password: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  login: (username: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  myWorlds: (token: string) => request<WorldSummary[]>("/worlds/my", undefined, token),
  createWorld: (token: string, payload: { code: string; name: string; is_public: boolean }) =>
    request<WorldSummary>("/worlds", { method: "POST", body: JSON.stringify(payload) }, token),
  joinWorld: (token: string, code: string) =>
    request<WorldSummary>("/worlds/join", { method: "POST", body: JSON.stringify({ code }) }, token),
  snapshot: (token: string, worldId: number) =>
    request<WorldSnapshot>(`/worlds/${worldId}/snapshot`, undefined, token),
};

export function wsUrl(worldCode: string, token: string): string {
  const base = (import.meta.env.VITE_WS_BASE ?? "ws://localhost:8000").replace(/\/$/, "");
  return `${base}/ws/world/${worldCode}?token=${encodeURIComponent(token)}`;
}
