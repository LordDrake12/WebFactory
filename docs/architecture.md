# Architecture Overview

## Stack

- **Frontend:** React + TypeScript + HTML Canvas
- **Backend:** FastAPI (REST + WebSocket)
- **DB:** SQLite
- **Hosting:** self-host on one server (reverse proxy optional)

## Multiplayer world model

- Users authenticate with username/password.
- A user creates worlds with a unique string `code`.
- Worlds are persistent in SQLite.
- Each world runs simulation ticks when at least one player is connected.
- Any member can join by world code.
- Admin role can edit world settings and world expansion.

## Runtime simulation model

- `WorldRuntimeManager` keeps hot in-memory world states.
- World state is autosaved to SQLite when marked dirty.
- Simulation loop ticks at a configurable rate.

## Extensibility model

### Items

Define all item metadata in `app/simulation/items.py` via `ItemDefinition` and `ItemRegistry`.

### Buildings

- Register metadata with `BuildingDefinition`.
- Attach behavior classes with `BuildingBehavior.tick(...)`.
- Place/remove handled by `WorldState`.

### Utilities

- Inventory utilities in `app/simulation/inventory.py` support stack limits, transfer, and extraction.
- Use these to implement production chains (miners, smelters, assemblers, etc.).
