from fastapi import HTTPException, status
import uuid
from app.models.model import Event, Category, Venue
from sqlalchemy import select
from app.schemas import event_schemas

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.core.redis import redis_client

async def create_event(db: AsyncSession, event_details: event_schemas.EventCreate,organizer_id: uuid.UUID):
    category = await db.get(Category, event_details.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    venue = await db.get(Venue, event_details.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    result = Event(**event_details.model_dump(),organizer_id=organizer_id)
    
    db.add(result)
    await db.commit()
    await db.refresh(result)

    await redis_client.delete("event:all")

    query = (
        select(Event)
        .options(
            selectinload(Event.organizer),
            selectinload(Event.category),
            selectinload(Event.venue),
        )
        .where(Event.id == result.id)
    )
    res = await db.execute(query)
    return res.scalars().first()

async def get_all_events(db: AsyncSession):
    result = await db.execute(select(Event).options(
        selectinload(Event.organizer),
        selectinload(Event.category),
        selectinload(Event.venue),
    ).order_by(Event.created_at.desc()))

    return result.scalars().all()

async def get_event_by_id(db: AsyncSession, event_id: uuid.UUID):
    result = await db.execute(select(Event).options(
        selectinload(Event.organizer),
        selectinload(Event.category),
        selectinload(Event.venue),
    ).where(Event.id == event_id))
    event = result.scalars().first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

async def update_event(db: AsyncSession, event_id: uuid.UUID, event_details: event_schemas.EventUpdate):
    category = await db.get(Category, event_details.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    venue = await db.get(Venue, event_details.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    event = await get_event_by_id(db, event_id)

    for field, value in event_details.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)

    await redis_client.delete("event:all")

    return event

async def delete_event(db: AsyncSession, event_id: uuid.UUID):
    event_data = await db.execute(select(Event).where(Event.id == event_id))
    event = event_data.scalars().first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    await db.delete(event)
    await db.commit()

    await redis_client.delete("event:all")

    return {"message": "Event deleted successfully"}