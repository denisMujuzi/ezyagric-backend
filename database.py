# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Use SQLite database
DATABASE_URL = "sqlite:///./sqlitedb.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
