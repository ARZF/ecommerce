from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    description: str


# Dummy products for testing
DUMMY_PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "description": "High-performance laptop"},
    {"id": 2, "name": "Mouse", "price": 29.99, "description": "Wireless mouse"},
    {"id": 3, "name": "Keyboard", "price": 79.99, "description": "Mechanical keyboard"},
    {"id": 4, "name": "Monitor", "price": 299.99, "description": "27-inch 4K monitor"},
    {"id": 5, "name": "Headphones", "price": 149.99, "description": "Noise-canceling headphones"},
]


@router.get("/", response_model=List[ProductOut])
def get_products():
    """Get all products - dummy data for testing"""
    return DUMMY_PRODUCTS

