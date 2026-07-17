from datetime import datetime
from fastapi import HTTPException, status
import uuid
from app.models.model import User
from sqlalchemy import select
from app.schemas import user_schemas

from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

passlib_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def user_create(db:AsyncSession,user_details:user_schemas.UserCreate):
    user = User(
        first_name=user_details.first_name,
        last_name=user_details.last_name,
        email=user_details.email,
        phone_number=user_details.phone_number,
        hashed_password=passlib_context.hash(user_details.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user(db:AsyncSession):
    user = await db.execute(select(User))
    return user.scalars().all()

async def get_by_id(db:AsyncSession,user_id: uuid.UUID):
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalars().first()

async def get_by_email(db:AsyncSession,email:str):
    user = await db.execute(select(User).where(User.email == email))
    return user.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: uuid.UUID, user_details: user_schemas.UserUpdate):
    user = await get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_details.model_dump(exclude_unset=True)

    if "email" in update_data:
        details = await get_by_email(db, update_data["email"])
        if details and details.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    for key, value in update_data.items():
        if key == "password":
            user.hashed_password = passlib_context.hash(value)
        else:
            setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db:AsyncSession,user_id:uuid.UUID):
    user = await get_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message":"User deleted successfully"}