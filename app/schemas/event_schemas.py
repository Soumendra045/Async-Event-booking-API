import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EventBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str

    category_id: uuid.UUID
    venue_id: uuid.UUID

    start_time: datetime
    end_time: datetime

    capacity: int = Field(..., gt=0)
    available_seats: int = Field(..., gt=0)
    ticket_price: Decimal = Field(..., ge=0)

    is_active: bool = True

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value, info):
        start_time = info.data.get("start_time")

        if start_time and value <= start_time:
            raise ValueError(
                "End time must be greater than start time."
            )

        return value


class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None

    category_id: Optional[uuid.UUID] = None
    venue_id: Optional[uuid.UUID] = None

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    capacity: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[Decimal] = Field(None, ge=0)

    is_active: Optional[bool] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value, info):
        start_time = info.data.get("start_time")

        if start_time and value and value <= start_time:
            raise ValueError(
                "End time must be greater than start time."
            )

        return value

class UserDetails(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class CategoryDetails(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class VenueDetails(BaseModel):
    id: uuid.UUID
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    capacity: int

    model_config = {
        "from_attributes": True
    }

class EventResponse(BaseModel):
    id: uuid.UUID

    title: str
    description: str

    organizer: UserDetails
    category: CategoryDetails
    venue: VenueDetails

    start_time: datetime
    end_time: datetime

    capacity: int
    available_seats: int

    ticket_price: Decimal
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class EventListResponse(BaseModel):
    events: list[EventResponse]