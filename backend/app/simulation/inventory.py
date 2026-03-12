from __future__ import annotations

from dataclasses import dataclass, field

from app.simulation.items import item_registry


@dataclass
class ItemStack:
    item_key: str
    amount: int


@dataclass
class Inventory:
    slots: int
    stacks: list[ItemStack] = field(default_factory=list)

    def can_insert(self, item_key: str, amount: int) -> bool:
        item_def = item_registry.get(item_key)
        total_capacity = 0
        existing = 0
        for stack in self.stacks:
            if stack.item_key == item_key:
                existing += stack.amount
                total_capacity += item_def.max_stack
        empty_slots = self.slots - len(self.stacks)
        total_capacity += empty_slots * item_def.max_stack
        return existing + amount <= total_capacity

    def insert(self, item_key: str, amount: int) -> int:
        if amount <= 0:
            return 0

        item_def = item_registry.get(item_key)
        remaining = amount

        for stack in self.stacks:
            if stack.item_key != item_key or remaining == 0:
                continue
            space = item_def.max_stack - stack.amount
            moved = min(space, remaining)
            stack.amount += moved
            remaining -= moved

        while remaining > 0 and len(self.stacks) < self.slots:
            moved = min(item_def.max_stack, remaining)
            self.stacks.append(ItemStack(item_key=item_key, amount=moved))
            remaining -= moved

        return amount - remaining

    def extract(self, item_key: str, amount: int) -> int:
        if amount <= 0:
            return 0

        remaining = amount
        for stack in list(self.stacks):
            if stack.item_key != item_key or remaining == 0:
                continue
            moved = min(stack.amount, remaining)
            stack.amount -= moved
            remaining -= moved
            if stack.amount == 0:
                self.stacks.remove(stack)

        return amount - remaining


def transfer(source: Inventory, target: Inventory, item_key: str, amount: int) -> int:
    moved_out = source.extract(item_key, amount)
    moved_in = target.insert(item_key, moved_out)
    if moved_in < moved_out:
        source.insert(item_key, moved_out - moved_in)
    return moved_in
