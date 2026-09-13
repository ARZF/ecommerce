"""Runnable check for the order routes — no test framework, no fixtures.

Run from the service dir (the same cwd uvicorn uses):
    python check_orders.py

Points the app's SQLite file at a temp dir first, so it never touches order_service.db.
"""
import atexit
import os
import shutil
import sys
import tempfile

_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SERVICE_DIR)
sys.path.insert(0, os.path.dirname(_SERVICE_DIR))  # repo root, so `common` resolves

_workdir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, _workdir, ignore_errors=True)
os.chdir(_workdir)

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


client = TestClient(app)

assert client.get("/").json() == {"service": "order", "status": "running"}
assert client.get("/orders/").json() == []

# create — status defaults to "pending", all fields come back
created = client.post(
    "/orders/",
    json={"user_id": 1, "product_id": 2, "quantity": 3, "total_price": 29.97},
)
assert created.status_code == 201, created.text
order = created.json()
assert order["status"] == "pending", order
assert (order["user_id"], order["product_id"], order["quantity"], order["total_price"]) == (1, 2, 3, 29.97), order
assert order["created_at"], order

# create — an explicit status is kept
assert client.post(
    "/orders/", json={"user_id": 2, "product_id": 9, "quantity": 1, "total_price": 5.0, "status": "paid"}
).json()["status"] == "paid"

# validation — quantity must be >= 1, price >= 0
assert client.post(
    "/orders/", json={"user_id": 1, "product_id": 2, "quantity": 0, "total_price": 1.0}
).status_code == 422
assert client.post(
    "/orders/", json={"user_id": 1, "product_id": 2, "quantity": 1, "total_price": -1.0}
).status_code == 422

# GET /orders/ lists both, oldest first
assert [o["id"] for o in client.get("/orders/").json()] == [order["id"], order["id"] + 1]

# GET /orders/user/{user_id} filters, and is empty (not 404) for a user with no orders
mine = client.get("/orders/user/1").json()
assert [o["id"] for o in mine] == [order["id"]], mine
assert all(o["user_id"] == 1 for o in mine)
assert client.get("/orders/user/99").json() == []

# GET /orders/{id} — found, and 404 for an unknown id
assert client.get(f"/orders/{order['id']}").json()["id"] == order["id"]
assert client.get("/orders/999").status_code == 404

# PUT /orders/{id} — partial: only the sent fields change
updated = client.put(f"/orders/{order['id']}", json={"status": "shipped", "quantity": 5})
assert updated.status_code == 200, updated.text
assert updated.json()["status"] == "shipped"
assert updated.json()["quantity"] == 5
assert updated.json()["total_price"] == 29.97  # not sent -> unchanged
assert client.put("/orders/999", json={"status": "x"}).status_code == 404

# DELETE /orders/{id} — 204, then gone; second delete is a 404
assert client.delete(f"/orders/{order['id']}").status_code == 204
assert client.get(f"/orders/{order['id']}").status_code == 404
assert client.delete(f"/orders/{order['id']}").status_code == 404

print("order_service check: all assertions passed")
