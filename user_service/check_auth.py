"""Runnable check for user auth (hashing + JWT config) — no test framework.

Run from the service dir (the same cwd uvicorn uses):
    python check_auth.py

Points the app's SQLite file at a temp dir first, so it never touches user_service.db.
"""
import atexit
import os
import shutil
import sys
import tempfile

_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SERVICE_DIR)
sys.path.insert(0, os.path.dirname(_SERVICE_DIR))  # repo root, so `common` resolves

# Set before importing the app, so common.config reads it
os.environ["JWT_SECRET"] = "check-secret-not-the-dev-fallback"

_workdir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, _workdir, ignore_errors=True)
os.chdir(_workdir)

from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402
from common.config import JWT_SECRET  # noqa: E402
from app.main import app  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models.user_model import User  # noqa: E402


client = TestClient(app)

# common.config honours the env var
assert JWT_SECRET == "check-secret-not-the-dev-fallback", JWT_SECRET

# create — the password must never come back in the response
created = client.post("/users/", json={"email": "a@example.com", "password": "hunter2"})
assert created.status_code == 201, created.text
assert "password_hash" not in created.json() and "password" not in created.json(), created.json()

# the stored value is a bcrypt hash, not the plaintext
with SessionLocal() as db:
    stored = db.query(User).filter(User.email == "a@example.com").first().password_hash
assert stored != "hunter2", stored
assert stored.startswith("$2b$") and len(stored) == 60, stored

# login — right password mints a token signed with the env secret
login = client.post("/users/login", json={"email": "a@example.com", "password": "hunter2"})
assert login.status_code == 200, login.text
token = login.json()["access_token"]
assert login.json()["token_type"] == "bearer", login.json()
claims = jwt.decode(token, "check-secret-not-the-dev-fallback", algorithms=["HS256"])
assert claims["email"] == "a@example.com" and claims["sub"] and claims["exp"], claims

# login — wrong password and unknown email are both 401
assert client.post(
    "/users/login", json={"email": "a@example.com", "password": "wrong"}
).status_code == 401
assert client.post(
    "/users/login", json={"email": "nobody@example.com", "password": "hunter2"}
).status_code == 401

# update re-hashes: the new password works, the old one stops working
updated = client.put("/users/1", json={"password": "newpass"})
assert updated.status_code == 200, updated.text
with SessionLocal() as db:
    rehashed = db.query(User).filter(User.id == 1).first().password_hash
assert rehashed != stored, "password_hash was not re-hashed on update"
assert client.post(
    "/users/login", json={"email": "a@example.com", "password": "newpass"}
).status_code == 200
assert client.post(
    "/users/login", json={"email": "a@example.com", "password": "hunter2"}
).status_code == 401

# a row holding a pre-hashing plaintext password gets a clean 401, not a 500
with SessionLocal() as db:
    db.add(User(email="legacy@example.com", password_hash="plaintext123"))
    db.commit()
legacy = client.post("/users/login", json={"email": "legacy@example.com", "password": "plaintext123"})
assert legacy.status_code == 401, f"expected 401, got {legacy.status_code}: {legacy.text}"

print("user_service auth check: all assertions passed")
