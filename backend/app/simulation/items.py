from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ItemDefinition:
    key: str
    name: str
    max_stack: int = 100


class ItemRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ItemDefinition] = {}

    def register(self, item: ItemDefinition) -> None:
        if item.key in self._items:
            raise ValueError(f"Item {item.key} already registered")
        self._items[item.key] = item

    def get(self, key: str) -> ItemDefinition:
        if key not in self._items:
            raise KeyError(f"Unknown item: {key}")
        return self._items[key]

    def all(self) -> list[ItemDefinition]:
        return list(self._items.values())


item_registry = ItemRegistry()

# Seed examples you can build from.
item_registry.register(ItemDefinition(key="ore.iron", name="Iron Ore"))
item_registry.register(ItemDefinition(key="ingot.iron", name="Iron Ingot"))
