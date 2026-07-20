from app.schemas import venue_schemas
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.dependancy import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.auth import get_current_user
from app.repositories import venue_repository

from app.services import venue_services

import uuid

router = APIRouter(
    prefix="/venues",
    tags=["Venues"]
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/create_venue', status_code=status.HTTP_201_CREATED, response_model=venue_schemas.VenueResponse)
async def create_venue_controller(
    venue_details: venue_schemas.VenueCreate,
    db: db_dependency,
    user: user_dependency
):

    if user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a venue"
        )
    venue = await venue_repository.create_venue(db, venue_details)
    return venue

@router.get('/get_all_user', response_model=list[venue_schemas.VenueResponse])
async def get_all_user(
    db: db_dependency,
    user: user_dependency
):

    venues = await venue_services.get_all_venues(db)
    return venues

@router.get('/get_venue_by_id/{venue_id}', response_model=venue_schemas.VenueResponse)
async def get_by_venue_id(
    db: db_dependency,
    venue_id: uuid.UUID,
    user: user_dependency
):

    venue = await venue_repository.get_venue_by_id(db, venue_id)
    return venue

@router.put('/update_venue/{venue_id}', response_model=venue_schemas.VenueResponse)
async def update_venue_controller(
    db: db_dependency,
    venue_id: uuid.UUID,
    user: user_dependency,
    venue_details: venue_schemas.VenueUpdate
):

    if user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update a venue"
        )
    venue = await venue_repository.update_venue(db, venue_id, venue_details)
    return venue

@router.delete('/delete_venue/{venue_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue_controller(
    db: db_dependency,
    venue_id: uuid.UUID,
    user: user_dependency
):

    if user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete a venue"
        )
    await venue_repository.delete_venue(db, venue_id)
    return {
        "message": "Venue deleted successfully"
    }

@router.get('/search_by_name/{name}', response_model=list[venue_schemas.VenueResponse])
async def search_by_name(
    db: db_dependency,
    name: str,
    user: user_dependency
):

    venues = await venue_repository.search_by_name(db, name)
    if venues:
        return venues
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No venue found with the given name"
        )