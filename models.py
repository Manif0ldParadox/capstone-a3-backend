from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="operator", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class InspectionSession(Base):
    __tablename__ = "inspection_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=False, default="Camera 1")
    status = Column(String, nullable=False, default="active")
    started_at = Column(DateTime, default=datetime.utcnow)


class InspectionResult(Base):
    __tablename__ = "inspection_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    length_mm = Column(Float, nullable=False)
    width_mm = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    source = Column(String, nullable=False, default="Camera 1")
    notes = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    live_camera = Column(Boolean, default=True, nullable=False)
    auto_save = Column(Boolean, default=False, nullable=False)
    ng_notification = Column(Boolean, default=True, nullable=False)
    sound_alert = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)