from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.db.base import SessionLocal
from app.models.entities import User, World, WorldMembership
from app.services.auth import decode_token
from app.services.realtime import socket_hub
from app.services.world_runtime import world_runtime_manager

router = APIRouter(tags=["ws"])


async def _get_user_from_token(token: str) -> User | None:
    payload = decode_token(token)
    user_id = int(payload["sub"])
    async with SessionLocal() as session:
        return await session.scalar(select(User).where(User.id == user_id))


@router.websocket("/ws/world/{code}")
async def world_socket(ws: WebSocket, code: str, token: str) -> None:
    try:
        user = await _get_user_from_token(token)
        if not user:
            await ws.close(code=1008)
            return

        async with SessionLocal() as session:
            world = await session.scalar(select(World).where(World.code == code))
            if not world:
                await ws.close(code=1008)
                return
            membership = await session.scalar(
                select(WorldMembership).where(
                    WorldMembership.world_id == world.id,
                    WorldMembership.user_id == user.id,
                )
            )
            if not membership:
                await ws.close(code=1008)
                return

        runtime = await world_runtime_manager.connect_user(world.id, user.id)
        await socket_hub.connect(world.id, ws)

        await ws.send_text(json.dumps({"type": "snapshot", "state": runtime.world_state.to_dict()}))

        while True:
            raw = await ws.receive_text()
            event = json.loads(raw)
            etype = event.get("type")

            if etype == "place_building":
                runtime.world_state.place(
                    def_key=event["def_key"],
                    x=int(event["x"]),
                    y=int(event["y"]),
                    rotation=int(event.get("rotation", 0)),
                )
                await world_runtime_manager.mark_dirty(world.id)
                await socket_hub.broadcast(world.id, {"type": "snapshot", "state": runtime.world_state.to_dict()})
            elif etype == "remove_building":
                runtime.world_state.remove(event["building_id"])
                await world_runtime_manager.mark_dirty(world.id)
                await socket_hub.broadcast(world.id, {"type": "snapshot", "state": runtime.world_state.to_dict()})

    except WebSocketDisconnect:
        pass
    except Exception:
        await ws.close(code=1011)
    finally:
        async with SessionLocal() as session:
            world = await session.scalar(select(World).where(World.code == code))
            if world:
                socket_hub.disconnect(world.id, ws)
                if "user" in locals() and user:
                    await world_runtime_manager.disconnect_user(world.id, user.id)
