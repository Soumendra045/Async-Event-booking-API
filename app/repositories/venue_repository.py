from app.db.dependancy import get_db
from typing import Annotated
# from datetime import datetime
from fastapi import HTTPException, status, Depends
import uuid
from app.models.model import Venue
from sqlalchemy import select
from app.schemas import venue_schemas

from sqlalchemy.ext.asyncio import AsyncSession


async def create_venue(db: AsyncSession, venue_details: venue_schemas.VenueCreate):
    venue = Venue(**venue_details.model_dump())

    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    return venue

async def get_all_venues(db: AsyncSession):
    results = await db.execute(select(Venue).order_by(Venue.created_at.desc()))

    return results.scalars().all()

async def get_venue_by_id(db: AsyncSession, venue_id: uuid.UUID):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))

    venue = result.scalars().first()

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return venue

async def update_venue(db: AsyncSession, venue_id: uuid.UUID, venue_details: venue_schemas.VenueUpdate):
    venue = await get_venue_by_id(db, venue_id)

    for field, value in venue_details.model_dump(exclude_unset=True).items():
        setattr(venue, field, value)

    await db.commit()
    await db.refresh(venue)
    return venue

async def delete_venue(db: AsyncSession, venue_id: uuid.UUID):
    venue = await get_venue_by_id(db, venue_id)

    await db.delete(venue)
    await db.commit()
    return {"message": "Venue deleted successfully"}

async def search_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Venue).where(Venue.name.ilike(f"%{name}%")))
    return result.scalars().all()
