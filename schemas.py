from pydantic import BaseModel, EmailStr
from datetime import datetime


# =========================
# AUTH
# =========================

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "operator"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# DASHBOARD
# =========================

class DashboardRecentInspection(BaseModel):
    id: int
    session_id: str
    length_mm: float
    width_mm: float
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_inspections: int
    ok_count: int
    ng_count: int
    ng_rate: float
    recent_inspections: list[DashboardRecentInspection]


# =========================
# INSPECTION START
# =========================

class InspectionStartRequest(BaseModel):
    source: str = "Camera 1"


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
    source: str
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

class HistoryItem(BaseModel):
    id: int
    session_id: str
    length_mm: float
    width_mm: float
    status: str
    source: str
    notes: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    data: list[HistoryItem]


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