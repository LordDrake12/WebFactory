from __future__ import annotations

from dataclasses import asdict, dataclass, field
from uuid import uuid4

from app.simulation.buildings import BuildingInstance, building_registry


@dataclass
class WorldState:
    width: int
    height: int
    buildings: dict[str, BuildingInstance] = field(default_factory=dict)

    def can_place(self, def_key: str, x: int, y: int) -> bool:
        if x < 0 or y < 0:
            return False
        definition = building_registry.get_definition(def_key)
        if x + definition.width > self.width or y + definition.height > self.height:
            return False
        for inst in self.buildings.values():
            other = building_registry.get_definition(inst.def_key)
            overlap = not (
                x + definition.width <= inst.x
                or inst.x + other.width <= x
                or y + definition.height <= inst.y
                or inst.y + other.height <= y
            )
            if overlap:
                return False
        return True

    def place(self, def_key: str, x: int, y: int, rotation: int = 0) -> str:
        if not self.can_place(def_key, x, y):
            raise ValueError("Invalid placement")
        inst = BuildingInstance(id=str(uuid4()), def_key=def_key, x=x, y=y, rotation=rotation)
        self.buildings[inst.id] = inst
        return inst.id

    def remove(self, building_id: str) -> None:
        self.buildings.pop(building_id, None)

    def tick(self, delta: float) -> None:
        for inst in list(self.buildings.values()):
            behavior = building_registry.get_behavior(inst.def_key)
            behavior.tick(inst, self, delta)

    def expand(self, add_w: int, add_h: int) -> None:
        self.width += add_w
        self.height += add_h

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "buildings": [
                {
                    **asdict(inst),
                    "input_inv": [asdict(s) for s in inst.input_inv.stacks],
                    "output_inv": [asdict(s) for s in inst.output_inv.stacks],
                }
                for inst in self.buildings.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict, default_w: int, default_h: int) -> "WorldState":
        world = cls(width=data.get("width", default_w), height=data.get("height", default_h))
        for raw in data.get("buildings", []):
            inst = BuildingInstance(
                id=raw["id"],
                def_key=raw["def_key"],
                x=raw["x"],
                y=raw["y"],
                rotation=raw.get("rotation", 0),
                data=raw.get("data", {}),
            )
            world.buildings[inst.id] = inst
        return world
