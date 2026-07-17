from pydantic import BaseModel, Field, ConfigDict
from  datetime import datetime
import uuid

class VenueBase(BaseModel):
    name: str = Field(..., examples=["My Venue"])
    address: str = Field(..., examples=["123 Main St"])
    city: str = Field(..., examples=["New York"])
    state: str = Field(..., examples=["NY"])
    country: str = Field(..., examples=["USA"])
    postal_code: str = Field(..., examples=["10001"])
    capacity: int = Field(..., examples=[100])

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class VenueCreate(VenueBase):
    pass

class VenueResponse(VenueBase):
    id: uuid.UUID

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True

class VenueUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    capacity: int | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )
    

