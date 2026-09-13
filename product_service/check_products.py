"""Runnable check for the product routes — no test framework, no fixtures.

Run from the service dir (the same cwd uvicorn uses):
    python check_products.py

Points the app's SQLite file at a temp dir first, so it never touches product_service.db.
"""
import atexit
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_workdir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, _workdir, ignore_errors=True)
os.chdir(_workdir)

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.seed import DUMMY_PRODUCTS, seed_products  # noqa: E402


client = TestClient(app)

assert client.get("/").json() == {"service": "product", "status": "running"}

# startup seeding — the 5 original products, ids 1-5, with the fields the frontend reads
seeded = client.get("/products/").json()
assert [p["id"] for p in seeded] == [1, 2, 3, 4, 5], seeded
assert [(p["name"], p["price"]) for p in seeded] == [(p["name"], p["price"]) for p in DUMMY_PRODUCTS], seeded
for product in seeded:
    assert product["name"] and isinstance(product["price"], float) and product["description"], product
    assert product["stock"] == 0, product  # column default
    assert product["created_at"], product

# seeding again must not duplicate
with SessionLocal() as db:
    seed_products(db)
assert len(client.get("/products/").json()) == 5

# GET /products/{id} — found, and 404 for an unknown id
first = client.get("/products/1").json()
assert (first["name"], first["price"]) == ("Laptop", 999.99), first
assert client.get("/products/999").status_code == 404

# POST /products/ — 201, stock defaults to 0 when omitted
created = client.post(
    "/products/", json={"name": "Webcam", "price": 59.5, "description": "1080p webcam"}
)
assert created.status_code == 201, created.text
product = created.json()
assert product["id"] == 6 and product["stock"] == 0, product
assert len(client.get("/products/").json()) == 6

# validation — price and stock must be >= 0, name/price/description required
assert client.post(
    "/products/", json={"name": "X", "price": -1.0, "description": "d"}
).status_code == 422
assert client.post(
    "/products/", json={"name": "X", "price": 1.0, "description": "d", "stock": -1}
).status_code == 422
assert client.post("/products/", json={"price": 1.0, "description": "d"}).status_code == 422

# PUT /products/{id} — partial: only the sent fields change
updated = client.put(f"/products/{product['id']}", json={"price": 49.99, "stock": 12})
assert updated.status_code == 200, updated.text
assert updated.json()["price"] == 49.99 and updated.json()["stock"] == 12
assert updated.json()["name"] == "Webcam"  # not sent -> unchanged
assert client.put("/products/999", json={"stock": 1}).status_code == 404

# DELETE /products/{id} — 204, then gone; second delete is a 404
assert client.delete(f"/products/{product['id']}").status_code == 204
assert client.get(f"/products/{product['id']}").status_code == 404
assert client.delete(f"/products/{product['id']}").status_code == 404
assert len(client.get("/products/").json()) == 5

print("product_service check: all assertions passed")
