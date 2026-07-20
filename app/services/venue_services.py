from app.core.redis import redis_client
from app.schemas.venue_schemas import VenueResponse
from app.repositories import venue_repository
import json
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

async def get_all_venues(db: AsyncSession):
    cached_venues = await redis_client.get("venues:all")
    if cached_venues:
        return json.loads(cached_venues)
    venues = await venue_repository.get_all_venues(db)
    venue_data = [
        VenueResponse.model_validate(venue).model_dump()
        for venue in venues
    ]
    json_data = jsonable_encoder(venue_data)
    await redis_client.set(
        "venues:all",
        json.dumps(json_data),
        ex=900
    )
    return json_data