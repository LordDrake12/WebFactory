import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { api, wsUrl } from "./api/client";
import type { WorldSnapshot, WorldSummary } from "./types";

const PINNED_CODES_KEY = "webfactory.pinnedCodes";

function loadPinnedCodes(): string[] {
  try {
    return JSON.parse(localStorage.getItem(PINNED_CODES_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function savePinnedCode(code: string) {
  const existing = loadPinnedCodes();
  const next = [code, ...existing.filter((c) => c !== code)].slice(0, 25);
  localStorage.setItem(PINNED_CODES_KEY, JSON.stringify(next));
}

export default function App() {
  const [token, setToken] = useState<string>("");
  const [username, setUsername] = useState<string>("");
  const [worlds, setWorlds] = useState<WorldSummary[]>([]);
  const [activeWorld, setActiveWorld] = useState<WorldSummary | null>(null);
  const [snapshot, setSnapshot] = useState<WorldSnapshot | null>(null);
  const [joinCode, setJoinCode] = useState("");
  const [pinnedCodes, setPinnedCodes] = useState<string[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState("connector");
  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => setPinnedCodes(loadPinnedCodes()), []);

  const buildingPalette = useMemo(() => ["connector", "belt", "hub"], []);

  async function refreshWorlds(tok = token) {
    if (!tok) return;
    setWorlds(await api.myWorlds(tok));
  }

  async function handleAuth(e: FormEvent<HTMLFormElement>, mode: "login" | "register") {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const user = String(formData.get("username") ?? "");
    const pass = String(formData.get("password") ?? "");
    const result = mode === "login" ? await api.login(user, pass) : await api.register(user, pass);
    setToken(result.token);
    setUsername(result.username);
    await refreshWorlds(result.token);
  }

  async function createWorld(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    await api.createWorld(token, {
      code: String(formData.get("code")),
      name: String(formData.get("name")),
      is_public: Boolean(formData.get("is_public")),
    });
    await refreshWorlds();
  }

  async function joinWorld(codeOverride?: string) {
    const code = codeOverride ?? joinCode;
    if (!code) return;
    const world = await api.joinWorld(token, code);
    savePinnedCode(code);
    setPinnedCodes(loadPinnedCodes());
    setActiveWorld(world);
    const snap = await api.snapshot(token, world.id);
    setSnapshot(snap);
    connectWorldSocket(world.code);
  }

  function connectWorldSocket(code: string) {
    wsRef.current?.close();
    const ws = new WebSocket(wsUrl(code, token));
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "snapshot" && activeWorld) {
        setSnapshot({
          world: activeWorld,
          settings: {},
          state: data.state,
        });
      }
    };
    wsRef.current = ws;
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !snapshot) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const cell = 20;
    canvas.width = snapshot.state.width * cell;
    canvas.height = snapshot.state.height * cell;
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "#222";
    for (let x = 0; x <= snapshot.state.width; x += 1) {
      ctx.beginPath();
      ctx.moveTo(x * cell, 0);
      ctx.lineTo(x * cell, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= snapshot.state.height; y += 1) {
      ctx.beginPath();
      ctx.moveTo(0, y * cell);
      ctx.lineTo(canvas.width, y * cell);
      ctx.stroke();
    }

    for (const b of snapshot.state.buildings) {
      ctx.fillStyle = b.def_key === "hub" ? "#8e44ad" : b.def_key === "belt" ? "#2980b9" : "#27ae60";
      ctx.fillRect(b.x * cell + 1, b.y * cell + 1, cell - 2, cell - 2);
    }
  }, [snapshot]);

  function onCanvasClick(event: React.MouseEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current;
    if (!canvas || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || !snapshot) return;

    const rect = canvas.getBoundingClientRect();
    const cell = 20;
    const x = Math.floor((event.clientX - rect.left) / cell);
    const y = Math.floor((event.clientY - rect.top) / cell);
    wsRef.current.send(JSON.stringify({ type: "place_building", def_key: selectedBuilding, x, y, rotation: 0 }));
  }

  if (!token) {
    return (
      <div style={{ padding: 24, fontFamily: "sans-serif" }}>
        <h1>WebFactory</h1>
        <p>Multiplayer framework for your custom factory game content.</p>
        <div style={{ display: "flex", gap: 24 }}>
          <form onSubmit={(e) => handleAuth(e, "register")}>
            <h3>Register</h3>
            <input name="username" placeholder="username" />
            <input name="password" placeholder="password" type="password" />
            <button type="submit">Create account</button>
          </form>
          <form onSubmit={(e) => handleAuth(e, "login")}>
            <h3>Login</h3>
            <input name="username" placeholder="username" />
            <input name="password" placeholder="password" type="password" />
            <button type="submit">Login</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 16, fontFamily: "sans-serif" }}>
      <h2>Welcome, {username}</h2>
      <button onClick={() => refreshWorlds()}>Refresh worlds</button>

      <div style={{ display: "grid", gridTemplateColumns: "350px 1fr", gap: 16, marginTop: 16 }}>
        <div>
          <h3>Create world</h3>
          <form onSubmit={createWorld}>
            <input name="code" placeholder="world code" required />
            <input name="name" placeholder="world name" required />
            <label>
              <input name="is_public" type="checkbox" /> public
            </label>
            <button type="submit">Create</button>
          </form>

          <h3>Join by code</h3>
          <input value={joinCode} onChange={(e) => setJoinCode(e.target.value)} placeholder="world code" />
          <button onClick={() => joinWorld()}>Join</button>

          <h4>Pinned codes</h4>
          <ul>
            {pinnedCodes.map((code) => (
              <li key={code}>
                <button onClick={() => joinWorld(code)}>{code}</button>
              </li>
            ))}
          </ul>

          <h3>Your worlds</h3>
          <ul>
            {worlds.map((w) => (
              <li key={w.id}>
                <button onClick={() => joinWorld(w.code)}>{w.name} ({w.code})</button>
              </li>
            ))}
          </ul>
        </div>

        <div>
          {activeWorld ? <h3>World: {activeWorld.name}</h3> : <h3>Select or join a world</h3>}
          <div>
            {buildingPalette.map((b) => (
              <button key={b} onClick={() => setSelectedBuilding(b)} style={{ fontWeight: b === selectedBuilding ? "bold" : "normal" }}>
                {b}
              </button>
            ))}
          </div>
          <p>Click grid to place selected building.</p>
          <div style={{ overflow: "auto", border: "1px solid #444", maxHeight: "70vh" }}>
            <canvas ref={canvasRef} onClick={onCanvasClick} />
          </div>
        </div>
      </div>
    </div>
  );
}
