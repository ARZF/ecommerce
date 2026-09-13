from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    price: float = Field(..., ge=0)
    description: str


class ProductCreate(ProductBase):
    stock: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class ProductOut(ProductBase):
    id: int
    stock: int
    created_at: datetime

    class Config:
        from_attributes = True
