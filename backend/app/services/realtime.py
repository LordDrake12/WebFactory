from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket


class WorldSocketHub:
    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, world_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.connections[world_id].add(ws)

    def disconnect(self, world_id: int, ws: WebSocket) -> None:
        if world_id in self.connections:
            self.connections[world_id].discard(ws)

    async def broadcast(self, world_id: int, payload: dict) -> None:
        text = json.dumps(payload)
        for ws in list(self.connections.get(world_id, set())):
            await ws.send_text(text)


socket_hub = WorldSocketHub()
