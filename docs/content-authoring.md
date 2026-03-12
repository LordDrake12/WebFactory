# Content Authoring Guide

This project is intentionally a **framework**. You can add content by extending registries and behavior logic.

## Add a new item

Edit `backend/app/simulation/items.py`:

```python
item_registry.register(ItemDefinition(key="plate.iron", name="Iron Plate", max_stack=200))
```

## Add a new building definition

Edit `backend/app/simulation/buildings.py`:

```python
building_registry.register(
    BuildingDefinition(
        key="smelter.basic",
        name="Basic Smelter",
        width=2,
        height=2,
        input_slots=2,
        output_slots=2,
    ),
    behavior=BasicSmelterBehavior(),
)
```

## Add custom building behavior

Create a class implementing `BuildingBehavior`:

```python
class BasicSmelterBehavior(BuildingBehavior):
    def tick(self, inst: BuildingInstance, world: WorldState, delta: float) -> None:
        # 1) consume ore from input inventory
        # 2) advance progress timer in inst.data
        # 3) output ingot to output inventory
        ...
```

Tips:

- Use `inst.data` for progress state, recipe state, machine mode, etc.
- Use inventory helpers to enforce stack limits and movement.
- Keep behaviors deterministic to simplify multiplayer sync.

## World expansion

Admin can call `POST /api/worlds/{world_id}/expand`.

Use this to gate progression milestones (research, achievements, currency).

## Suggested next additions

- Recipe registry (`recipes.py`)
- Belt graph resolver/pathing
- Power network simulation
- Terrain/resources generation
- Blueprint import/export
