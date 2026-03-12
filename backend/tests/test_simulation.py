from app.simulation.inventory import Inventory, transfer
from app.simulation.world import WorldState


def test_inventory_transfer_roundtrip():
    source = Inventory(slots=2)
    target = Inventory(slots=1)

    inserted = source.insert("ore.iron", 120)
    assert inserted == 120

    moved = transfer(source, target, "ore.iron", 90)
    assert moved == 90
    assert source.extract("ore.iron", 999) == 30


def test_world_placement_and_expansion():
    world = WorldState(width=4, height=4)
    world.place("connector", 0, 0)

    assert not world.can_place("hub", 3, 3)
    world.expand(2, 2)
    assert world.can_place("hub", 3, 3)
