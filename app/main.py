from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import engine
from app.db.base_class import Base
from app.routers import user_router
from app.authentication import token_router
from app.routers import category_router
from app.routers import venue_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token_router.router)
app.include_router(user_router.router)
app.include_router(category_router.router)
app.include_router(venue_router.router)