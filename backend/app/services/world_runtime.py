from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select

from app.core.config import settings
from app.db.base import SessionLocal
from app.models.entities import World
from app.simulation.world import WorldState


@dataclass
class RuntimeWorld:
    world_id: int
    world_state: WorldState
    connected_users: set[int] = field(default_factory=set)
    dirty: bool = False
    task: asyncio.Task | None = None


class WorldRuntimeManager:
    def __init__(self) -> None:
        self._worlds: dict[int, RuntimeWorld] = {}
        self._world_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def load_world(self, world_id: int) -> RuntimeWorld:
        if world_id in self._worlds:
            return self._worlds[world_id]
        async with self._world_locks[world_id]:
            if world_id in self._worlds:
                return self._worlds[world_id]
            async with SessionLocal() as session:
                world = await session.scalar(select(World).where(World.id == world_id))
                if not world:
                    raise ValueError("World not found")
                state_data = json.loads(world.state_json or "{}")
                state = WorldState.from_dict(state_data, world.size_w, world.size_h)
                runtime = RuntimeWorld(world_id=world_id, world_state=state)
                self._worlds[world_id] = runtime
                return runtime

    async def connect_user(self, world_id: int, user_id: int) -> RuntimeWorld:
        runtime = await self.load_world(world_id)
        runtime.connected_users.add(user_id)
        if runtime.task is None or runtime.task.done():
            runtime.task = asyncio.create_task(self._run_world(world_id))
        return runtime

    async def disconnect_user(self, world_id: int, user_id: int) -> None:
        runtime = self._worlds.get(world_id)
        if not runtime:
            return
        runtime.connected_users.discard(user_id)
        if not runtime.connected_users:
            await self._save_world(runtime)

    async def mark_dirty(self, world_id: int) -> None:
        runtime = self._worlds.get(world_id)
        if runtime:
            runtime.dirty = True

    async def _run_world(self, world_id: int) -> None:
        runtime = self._worlds[world_id]
        tick_delta = 1 / settings.tick_rate_hz
        last_save = time.monotonic()

        while runtime.connected_users:
            runtime.world_state.tick(tick_delta)
            now = time.monotonic()
            if runtime.dirty and now - last_save >= settings.autosave_interval_seconds:
                await self._save_world(runtime)
                last_save = now
            await asyncio.sleep(tick_delta)

    async def _save_world(self, runtime: RuntimeWorld) -> None:
        async with SessionLocal() as session:
            world = await session.scalar(select(World).where(World.id == runtime.world_id))
            if not world:
                return
            state_dict = runtime.world_state.to_dict()
            world.state_json = json.dumps(state_dict)
            world.size_w = runtime.world_state.width
            world.size_h = runtime.world_state.height
            await session.commit()
            runtime.dirty = False


world_runtime_manager = WorldRuntimeManager()
