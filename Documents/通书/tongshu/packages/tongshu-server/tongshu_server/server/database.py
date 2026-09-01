# 数据库模型
from sqlalchemy import create_engine, Column, String, Date, DateTime, Float, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os, uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "tongshu.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, index=True)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    latitude = Column(Float, default=0)
    longitude = Column(Float, default=0)
    city = Column(String, default="")
    chart_json = Column(JSON)
    yongshen_json = Column(JSON)
    consent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyGuidance(Base):
    __tablename__ = "daily_guidance"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guid_date = Column(Date, nullable=False, index=True)
    profile_id = Column(String, nullable=True, index=True)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NFCTag(Base):
    __tablename__ = "nfc_tags"
    id = Column(String, primary_key=True)  # Tag UID
    profile_id = Column(String, index=True)
    product_sku = Column(String, default="")
    activated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)