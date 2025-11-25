from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import product_routes

app = FastAPI(title="Product Service")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(product_routes.router)

@app.get("/")
def root():
    return {"service": "product", "status": "running"}

