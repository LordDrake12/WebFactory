from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class World(Base):
    __tablename__ = "worlds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, default=16, nullable=False)
    size_w: Mapped[int] = mapped_column(Integer, default=64, nullable=False)
    size_h: Mapped[int] = mapped_column(Integer, default=64, nullable=False)
    expansion_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    state_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    owner: Mapped[User] = relationship()


class WorldMembership(Base):
    __tablename__ = "world_memberships"
    __table_args__ = (UniqueConstraint("world_id", "user_id", name="uq_world_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="player", nullable=False)

    world: Mapped[World] = relationship()
    user: Mapped[User] = relationship()
