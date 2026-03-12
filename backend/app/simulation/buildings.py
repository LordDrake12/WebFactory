from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.simulation.inventory import Inventory


@dataclass(frozen=True)
class BuildingDefinition:
    key: str
    name: str
    width: int = 1
    height: int = 1
    input_slots: int = 0
    output_slots: int = 0


@dataclass
class BuildingInstance:
    id: str
    def_key: str
    x: int
    y: int
    rotation: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    input_inv: Inventory = field(default_factory=lambda: Inventory(slots=4))
    output_inv: Inventory = field(default_factory=lambda: Inventory(slots=4))


class BuildingBehavior:
    def tick(self, inst: BuildingInstance, world: "WorldState", delta: float) -> None:
        raise NotImplementedError


class NoopBehavior(BuildingBehavior):
    def tick(self, inst: BuildingInstance, world: "WorldState", delta: float) -> None:
        return


class BuildingRegistry:
    def __init__(self) -> None:
        self._defs: dict[str, BuildingDefinition] = {}
        self._behaviors: dict[str, BuildingBehavior] = {}

    def register(self, definition: BuildingDefinition, behavior: BuildingBehavior | None = None) -> None:
        if definition.key in self._defs:
            raise ValueError(f"Building {definition.key} already registered")
        self._defs[definition.key] = definition
        self._behaviors[definition.key] = behavior or NoopBehavior()

    def get_definition(self, key: str) -> BuildingDefinition:
        return self._defs[key]

    def get_behavior(self, key: str) -> BuildingBehavior:
        return self._behaviors[key]

    def all_definitions(self) -> list[BuildingDefinition]:
        return list(self._defs.values())


building_registry = BuildingRegistry()

# Seed starter examples.
building_registry.register(BuildingDefinition(key="hub", name="Hub", width=2, height=2))
building_registry.register(BuildingDefinition(key="belt", name="Belt"))
building_registry.register(BuildingDefinition(key="connector", name="Connector"))
