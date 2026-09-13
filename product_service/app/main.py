from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import product_routes
from app.db import Base, SessionLocal, engine
from app.models import product_model  # noqa: F401 - ensure models are imported before create_all
from app.seed import seed_products

app = FastAPI(title="Product Service")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create database tables at startup (simple development convenience)
Base.metadata.create_all(bind=engine)

# Seed the original dummy products so the frontend has data on a fresh database
with SessionLocal() as db:
    seed_products(db)

app.include_router(product_routes.router)

@app.get("/")
def root():
    return {"service": "product", "status": "running"}
