from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(min_length=3, max_length=1000, default=None)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class CategoryResponse(CategoryCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )