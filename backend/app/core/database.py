from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os

#safely load the .env file 
package_env = Path(__file__).parent / ".env"
if package_env.exists():
    load_dotenv(package_env)
else:
   
    located = find_dotenv()
    if located:
        load_dotenv(located)

# safety check for Database Url 
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set.\n"
        "Put a .env file at backend/app/.env or export DATABASE_URL in your environment."
    )

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
) 

class Base(DeclarativeBase): pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()