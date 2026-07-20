import json
from app.core.redis import redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.repositories import event_repository
from app.schemas.event_schemas import EventResponse

async def get_all_events_service(db: AsyncSession):
    cached_data = await redis_client.get("event:all")
    if cached_data:
        return json.loads(cached_data)

    events = await event_repository.get_all_events(db)
    event_data = [
        EventResponse.model_validate(event).model_dump()
        for event in events
    ]
    json_data = jsonable_encoder(event_data)

    await redis_client.set(
        "event:all",
        json.dumps(json_data),
        ex=300
    )

    return json_data
    
