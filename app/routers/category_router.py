from uuid import UUID
from app.models.model import Category
from sqlalchemy import select
from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.auth import get_current_user
from app.db.dependancy import get_db
from app.schemas import category_schemas

from app.repositories import category_repository

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]

@router.post('/category-create', status_code=status.HTTP_201_CREATED, response_model=category_schemas.CategoryResponse)
async def create_category(db: db_dependency, user:user_dependency,category:category_schemas.CategoryCreate):
    if user.role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to create category")
    category_exits = await db.execute(select(Category).where(category.name == Category.name))
    if category_exits.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category already exists")
    return await category_repository.create_category(db, category)

@router.get('/get_all_category', response_model=list[category_schemas.CategoryResponse])
async def get_all_category(db: db_dependency, user: user_dependency):
    return await category_repository.get_category(db)

@router.get('/get_category_by_id', response_model=category_schemas.CategoryResponse)
async def get_category_by_id(db: db_dependency, user: user_dependency, category_id: UUID):
    category = await category_repository.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
    return category

@router.put('/update_category/{category_id}', response_model=category_schemas.CategoryResponse)
async def update_category(db: db_dependency, user:user_dependency,category_id:UUID,category:category_schemas.CategoryUpdate):
    if user.role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to update category")
    results =  await category_repository.update_category(db, category_id, category)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
    return results

@router.delete('/delete_category/{category_id}', status_code=status.HTTP_200_OK)
async def delete_category(db: db_dependency, user:user_dependency,category_id:UUID):
    if user.role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized to delete category")
    results =  await category_repository.delete_category(db, category_id)

    return {'message':f'{results.name} Category deleted successfully'}