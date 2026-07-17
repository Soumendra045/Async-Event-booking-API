# import uuid
import uuid
from app.models.model import User
from app.db.dependancy import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import user_repository
from app.schemas import user_schemas
from typing import Annotated, List

from sqlalchemy import select

from app.repositories import user_repository

from app.authentication.auth import get_current_user


router = APIRouter(
    tags=['users']
)

db_dependancy = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/signup",status_code=status.HTTP_201_CREATED,response_model=user_schemas.UserResponse)
async def create_user_schema(user_details:user_schemas.UserCreate, db:db_dependancy):
    email = await db.execute(select(User).where(user_details.email == User.email))
    if email.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists")
    user_create =  await user_repository.user_create(db, user_details)
    return user_create

@router.get("/get_all_users",status_code=status.HTTP_200_OK,response_model=List[user_schemas.UserResponse])
async def get_all_users(db:db_dependancy,user:user_dependency):
    if user.role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to access this resource")
    users = await user_repository.get_user(db)
    return users

@router.get("/get_user_details",status_code=status.HTTP_200_OK,response_model=user_schemas.UserResponse)
async def get_user_by_id(db:db_dependancy,user: user_dependency):
    user = await user_repository.get_by_id(db,user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user

@router.get("/get_user_by_email",status_code=status.HTTP_200_OK,response_model=user_schemas.UserResponse)
async def get_user_by_email(db:db_dependancy,email:str, user: user_dependency):
    if user.role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to access this resource")
    user = await user_repository.get_by_email(db,email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user

@router.put('/update_user/{user_id}',response_model=user_schemas.UserResponse,status_code=status.HTTP_200_OK)
async def update_user(db: db_dependancy, user_details: user_schemas.UserUpdate, user_id: uuid.UUID, user: user_dependency):
    if user.role != 'ADMIN' and user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to update user details")
    user_update = await user_repository.update_user(db, user_id, user_details)
    return user_update

@router.delete('/delete_user/{user_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependancy, user: user_dependency, user_id: uuid.UUID):
    if user.role != 'ADMIN' and user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to delete user details")
    await user_repository.delete_user(db, user_id)
    return {"message":"User deleted successfully"}