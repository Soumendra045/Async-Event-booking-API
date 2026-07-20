from fastapi import APIRouter, Depends, status, HTTPException
from app.repositories import event_repository
from app.schemas import event_schemas
from app.db.dependancy import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.auth import get_current_user
import uuid

from app.services import event_services


router = APIRouter(
    prefix='/events',
    tags=['events']
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/create_event', status_code=status.HTTP_201_CREATED, response_model=event_schemas.EventResponse)
async def create_event(db: db_dependency, event_details: event_schemas.EventCreate, user: user_dependency):
    if user.role not in ["ADMIN", "ORGANIZER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create an event."
        )
    return await event_repository.create_event(db, event_details, user.id)

@router.get('/get_all_events', response_model=list[event_schemas.EventResponse])
async def get_all_events(db: db_dependency,user:user_dependency):
    return await event_services.get_all_events_service(db)

@router.get('/get_event_by_id', response_model=event_schemas.EventResponse)
async def get_event_by_id(db: db_dependency, event_id: uuid.UUID,user: user_dependency):
    return await event_repository.get_event_by_id(db, event_id)

@router.put('/update_event', response_model=event_schemas.EventResponse)
async def update_event(db: db_dependency, event_id: uuid.UUID, event_details: event_schemas.EventUpdate, user: user_dependency):
    if user.role not in ["ADMIN", "ORGANIZER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update an event."
        )
    return await event_repository.update_event(db, event_id, event_details)

@router.delete('/delete_event',status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(db: db_dependency, event_id: uuid.UUID, user: user_dependency):
    if user.role not in ["ADMIN", "ORGANIZER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete an event."
        )
    await event_repository.delete_event(db, event_id)
    return {"message": "Event deleted successfully"}
