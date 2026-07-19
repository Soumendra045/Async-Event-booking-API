from app.core.redis import redis_client
from datetime import datetime
from fastapi import HTTPException, status
import uuid
from app.models.model import Category
from sqlalchemy import select
from app.schemas import category_schemas

from sqlalchemy.ext.asyncio import AsyncSession


async def create_category(db: AsyncSession, category: category_schemas.CategoryCreate):
    category_details = Category(**category.model_dump())

    db.add(category_details)
    await db.commit()
    await db.refresh(category_details)

    await redis_client.delete("categories:all")

    return category_details

async def get_category(db: AsyncSession):
    category = await db.execute(select(Category))
    return category.scalars().all()

async def get_category_by_id(db: AsyncSession, category_id: uuid.UUID):
    category = await db.execute(select(Category).where(Category.id == category_id))
    return category.scalars().first()

async def update_category(db: AsyncSession, category_id: uuid.UUID, category:category_schemas.CategoryUpdate):
    category_details = await get_category_by_id(db, category_id)
    if not category_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
    data = category.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category_details, key, value)
    
    await db.commit()
    await db.refresh(category_details)

    await redis_client.delete("categories:all")
    
    return category_details

async def delete_category(db: AsyncSession, category_id: uuid.UUID):
    category_details = await get_category_by_id(db, category_id)
    if not category_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")

    await db.delete(category_details)
    await db.commit()

    await redis_client.delete("categories:all")

    return category_details
