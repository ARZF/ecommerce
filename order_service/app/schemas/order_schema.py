from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(..., ge=1)
    total_price: float = Field(..., ge=0)


class OrderCreate(OrderBase):
    status: str = "pending"


class OrderUpdate(BaseModel):
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=1)
    total_price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None


class OrderOut(OrderBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
