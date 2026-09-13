import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import order_routes
from app.db import Base, engine
from app.models import order_model  # noqa: F401 - ensure models are imported before create_all
from app.events.order_events import consume_user_created


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Consume user.created in the background — proof the broker pipe works
    consumer = asyncio.create_task(consume_user_created())
    yield
    consumer.cancel()


app = FastAPI(title="Order Service", lifespan=lifespan)

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
