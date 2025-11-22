from datetime import datetime
from pydantic import BaseModel, Field


# ---------------- USERS ----------------

class UserBase(BaseModel):
    username: str
    full_name: str | None = None
    email: str | None = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------------- TICKETS ----------------

class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    status: str | None = "open"
    priority: str | None = "medium"


class TicketCreate(TicketBase):
    owner_id: int | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    owner_id: int | None = None


class Ticket(TicketBase):
    id: int
    owner_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
