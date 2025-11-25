from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Simple default to a local SQLite database for development.
# You can override via the DATABASE_URL environment variable later.
DATABASE_URL = "sqlite:///./user_service.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
