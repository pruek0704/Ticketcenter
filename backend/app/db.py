import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(os.environ.get("DATABASE_URL", "sqlite:///./ticketcenter.db"), pool_pre_ping=True)

def get_db():
    with Session(engine) as session:
        yield session

