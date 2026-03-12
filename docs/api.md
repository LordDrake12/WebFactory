# API Reference

## Auth

- `POST /api/auth/register`
- `POST /api/auth/login`

Returns `token` + `username`.

## Worlds

- `POST /api/worlds` create world
- `GET /api/worlds/my` list joined worlds
- `POST /api/worlds/join` join by code
- `GET /api/worlds/{world_id}/snapshot` world settings + map state
- `PATCH /api/worlds/{world_id}/settings` (admin)
- `POST /api/worlds/{world_id}/expand` (admin)
- `GET /api/worlds/discover/public`

## WebSocket

- `GET /ws/world/{code}?token=...`

### Client events

- `{"type":"place_building","def_key":"connector","x":1,"y":1,"rotation":0}`
- `{"type":"remove_building","building_id":"..."}`

### Server events

- `{"type":"snapshot","state":{...}}`

Current sync strategy sends full snapshots for simplicity; replace with deltas later for scale.
