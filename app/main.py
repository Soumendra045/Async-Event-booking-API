from app.core.redis import redis_client
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import engine
from app.db.base_class import Base
from app.authentication import token_router
from app.routers import venue_router, event_router,category_router, user_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await redis_client.ping()
    print("Redis connected successfully.")
    yield
    await engine.dispose()

    await redis_client.aclose()

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
app.include_router(event_router.router)