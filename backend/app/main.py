from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api.auth import router as auth_router
from app.api.worlds import router as worlds_router
from app.api.ws import router as ws_router
from app.core.config import settings
from app.db.base import Base, engine
from app.simulation.buildings import building_registry
from app.simulation.items import item_registry


app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def startup() -> None:
    await init_db(engine)


async def init_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "items": [i.key for i in item_registry.all()],
        "buildings": [b.key for b in building_registry.all_definitions()],
    }


app.include_router(auth_router, prefix="/api")
app.include_router(worlds_router, prefix="/api")
app.include_router(ws_router)


try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    pass
