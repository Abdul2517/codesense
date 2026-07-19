import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None
Base = declarative_base()

class PRReview(Base):
    __tablename__ = "pr_reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo = Column(String, index=True)
    pr_number = Column(Integer)
    pr_title = Column(String)
    verdict = Column(String)
    confidence = Column(Float)
    issues_count = Column(Integer, default=0)
    suggestions_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
        print("Database tables created")
    else:
        print("No DATABASE_URL found, skipping DB init")

def get_db():
    if not SessionLocal:
        return None
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e