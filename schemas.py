from pydantic import BaseModel, EmailStr
from datetime import datetime


# =========================
# USER
# =========================

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# =========================
# INSPECTION SESSION START
# =========================

class InspectionStartRequest(BaseModel):
    inspection_title: str
    worker_name: str
    product_line: str
    product_id: str
    inspection_type: str


class InspectionStartResponse(BaseModel):
    session_id: str


# =========================
# INSPECTION SAVE
# =========================

class InspectionCreate(BaseModel):
    session_id: str
    length_mm: float
    width_mm: float
    status: str
    source: str = "manual"
    notes: str = ""
    image_path: str | None = None


class InspectionResponse(BaseModel):
    id: int
    session_id: str
    length_mm: float
    width_mm: float
    status: str
    source: str
    notes: str | None = None
    image_path: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


# =========================
# HISTORY
# =========================

class HistoryResponse(BaseModel):
    total: int
    items: list[InspectionResponse]


# =========================
# DASHBOARD
# =========================

class DashboardResponse(BaseModel):
    total_inspections: int
    ok_count: int
    ng_count: int
    ng_rate: float
    recent_inspections: list[InspectionResponse]


# =========================
# SETTINGS
# =========================

class SettingsResponse(BaseModel):
    live_camera: bool
    auto_save: bool
    ng_notification: bool
    sound_alert: bool

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    live_camera: bool | None = None
    auto_save: bool | None = None
    ng_notification: bool | None = None
    sound_alert: bool | None = None