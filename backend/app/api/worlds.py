from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.base import get_session
from app.models.entities import User, World, WorldMembership
from app.schemas.world import (
    CreateWorldRequest,
    ExpandWorldRequest,
    JoinWorldRequest,
    UpdateWorldSettingsRequest,
    WorldSnapshot,
    WorldSummary,
)
from app.services.world_runtime import world_runtime_manager

router = APIRouter(prefix="/worlds", tags=["worlds"])


def to_summary(world: World) -> WorldSummary:
    return WorldSummary(
        id=world.id,
        code=world.code,
        name=world.name,
        owner_id=world.owner_id,
        is_public=world.is_public,
        max_players=world.max_players,
        size_w=world.size_w,
        size_h=world.size_h,
        expansion_level=world.expansion_level,
    )


@router.post("", response_model=WorldSummary)
async def create_world(
    payload: CreateWorldRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorldSummary:
    existing = await session.scalar(select(World).where(World.code == payload.code))
    if existing:
        raise HTTPException(status_code=409, detail="World code already used")

    world = World(
        code=payload.code,
        name=payload.name,
        owner_id=user.id,
        is_public=payload.is_public,
        settings={"dayNightCycle": False, "buildCostMultiplier": 1.0},
        max_players=settings.max_players_per_world,
        state_json=json.dumps({"width": 64, "height": 64, "buildings": []}),
    )
    session.add(world)
    await session.flush()

    membership = WorldMembership(world_id=world.id, user_id=user.id, role="admin")
    session.add(membership)

    await session.commit()
    await session.refresh(world)
    return to_summary(world)


@router.get("/my", response_model=list[WorldSummary])
async def my_worlds(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[WorldSummary]:
    query = (
        select(World)
        .join(WorldMembership, WorldMembership.world_id == World.id)
        .where(WorldMembership.user_id == user.id)
    )
    worlds = (await session.scalars(query)).all()
    return [to_summary(w) for w in worlds]


@router.post("/join", response_model=WorldSummary)
async def join_world(
    payload: JoinWorldRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorldSummary:
    world = await session.scalar(select(World).where(World.code == payload.code))
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    membership = await session.scalar(
        select(WorldMembership).where(
            WorldMembership.world_id == world.id, WorldMembership.user_id == user.id
        )
    )
    if not membership:
        session.add(WorldMembership(world_id=world.id, user_id=user.id, role="player"))
        await session.commit()

    return to_summary(world)


async def _ensure_member(session: AsyncSession, world_id: int, user_id: int) -> WorldMembership:
    membership = await session.scalar(
        select(WorldMembership).where(WorldMembership.world_id == world_id, WorldMembership.user_id == user_id)
    )
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this world")
    return membership


@router.get("/{world_id}/snapshot", response_model=WorldSnapshot)
async def get_snapshot(
    world_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorldSnapshot:
    await _ensure_member(session, world_id, user.id)
    world = await session.scalar(select(World).where(World.id == world_id))
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    state = json.loads(world.state_json)
    return WorldSnapshot(world=to_summary(world), settings=world.settings, state=state)


@router.patch("/{world_id}/settings", response_model=WorldSummary)
async def update_settings(
    world_id: int,
    payload: UpdateWorldSettingsRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorldSummary:
    membership = await _ensure_member(session, world_id, user.id)
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update settings")
    world = await session.scalar(select(World).where(World.id == world_id))
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    world.settings = payload.settings
    await session.commit()
    await session.refresh(world)
    return to_summary(world)


@router.post("/{world_id}/expand", response_model=WorldSummary)
async def expand_world(
    world_id: int,
    payload: ExpandWorldRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorldSummary:
    membership = await _ensure_member(session, world_id, user.id)
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can expand world")

    world = await session.scalar(select(World).where(World.id == world_id))
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    runtime = await world_runtime_manager.load_world(world.id)
    runtime.world_state.expand(payload.add_w, payload.add_h)
    runtime.dirty = True

    world.expansion_level += 1
    world.size_w = runtime.world_state.width
    world.size_h = runtime.world_state.height
    world.state_json = json.dumps(runtime.world_state.to_dict())

    await session.commit()
    await session.refresh(world)
    return to_summary(world)


@router.get("/discover/public", response_model=list[WorldSummary])
async def list_public_worlds(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[WorldSummary]:
    query = select(World).where(or_(World.is_public.is_(True), World.owner_id == user.id))
    worlds = (await session.scalars(query)).all()
    return [to_summary(w) for w in worlds]
