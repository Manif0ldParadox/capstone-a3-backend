from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="operator")


class InspectionSession(Base):
    __tablename__ = "inspection_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    inspection_title = Column(String, nullable=False)
    worker_name = Column(String, nullable=False)
    product_line = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    inspection_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class InspectionResult(Base):
    __tablename__ = "inspection_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    length_mm = Column(Float, nullable=False)
    width_mm = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    source = Column(String, nullable=False, default="manual")
    notes = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    live_camera = Column(Boolean, default=True)
    auto_save = Column(Boolean, default=False)
    ng_notification = Column(Boolean, default=True)
    sound_alert = Column(Boolean, default=True)