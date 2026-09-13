from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import order_routes
from app.db import Base, engine
from app.models import order_model  # noqa: F401 - ensure models are imported before create_all

app = FastAPI(title="Order Service")

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

app.include_router(order_routes.router)

@app.get("/")
def root():
    return {"service": "order", "status": "running"}
