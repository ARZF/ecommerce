from sqlalchemy.orm import Session

from app.models.product_model import Product


# The list /products used to hardcode, kept so the frontend still has data.
DUMMY_PRODUCTS = [
    {"name": "Laptop", "price": 999.99, "description": "High-performance laptop"},
    {"name": "Mouse", "price": 29.99, "description": "Wireless mouse"},
    {"name": "Keyboard", "price": 79.99, "description": "Mechanical keyboard"},
    {"name": "Monitor", "price": 299.99, "description": "27-inch 4K monitor"},
    {"name": "Headphones", "price": 149.99, "description": "Noise-canceling headphones"},
]


def seed_products(db: Session):
    """Insert the dummy products, but only into an empty table (ids 1-5)."""
    if db.query(Product).first() is not None:
        return
    db.add_all([Product(**product) for product in DUMMY_PRODUCTS])
    db.commit()
