import logging
import os
import csv
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import Base, engine, SessionLocal
from models import User, InspectionSession, InspectionResult, SystemSettings
from schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    DashboardResponse,
    InspectionStartRequest,
    InspectionStartResponse,
    InspectionCreate,
    InspectionResponse,
    HistoryResponse,
    SettingsResponse,
    SettingsUpdate,
)
from auth import hash_password, verify_password, create_access_token, decode_access_token


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Inspection Backend API",
    description="Backend API for Automated Dimensional Inspection System",
    version="1.0.0"
)

security = HTTPBearer()

os.makedirs("logs", exist_ok=True)
os.makedirs("exports", exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def ensure_default_settings(db: Session):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(
            live_camera=True,
            auto_save=False,
            ng_notification=True,
            sound_alert=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@app.get("/")
def read_root():
    return {"message": "Capstone API running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# =========================
# AUTH
# =========================

@app.post("/register", response_model=UserResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email sudah digunakan, silakan login"
    )

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role  # dibebaskan sesuai frontend
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered: {new_user.email}")
    return new_user


@app.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    logger.info(f"Login success: {user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# =========================
# DASHBOARD
# =========================

@app.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = db.query(InspectionResult).count()
    ok_count = db.query(InspectionResult).filter(InspectionResult.status == "OK").count()
    ng_count = db.query(InspectionResult).filter(InspectionResult.status == "NG").count()

    ng_rate = round((ng_count / total) * 100, 2) if total > 0 else 0.0

    recent = (
        db.query(InspectionResult)
        .order_by(InspectionResult.id.desc())
        .limit(5)
        .all()
    )

    return {
        "total_inspections": total,
        "ok_count": ok_count,
        "ng_count": ng_count,
        "ng_rate": ng_rate,
        "recent_inspections": recent
    }


# =========================
# INSPECTION
# =========================

@app.post("/inspection/start", response_model=InspectionStartResponse)
def start_inspection(
    payload: InspectionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session_id = f"S{str(uuid4().int)[:6]}"

    session = InspectionSession(
        session_id=session_id,
        inspection_title=payload.inspection_title,
        worker_name=payload.worker_name,
        product_line=payload.product_line,
        product_id=payload.product_id,
        inspection_type=payload.inspection_type,
        status="active"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Inspection session started: {session_id}")
    return {"session_id": session.session_id}


@app.post("/inspection-results", response_model=InspectionResponse)
def save_inspection(
    payload: InspectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(InspectionSession).filter(
        InspectionSession.session_id == payload.session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = InspectionResult(
        session_id=payload.session_id,
        length_mm=payload.length_mm,
        width_mm=payload.width_mm,
        status=payload.status,
        source=payload.source,
        notes=payload.notes,
        image_path=payload.image_path
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    logger.info(f"Inspection saved for session: {payload.session_id}")
    return result


# =========================
# HISTORY
# =========================

@app.get("/inspection-results", response_model=HistoryResponse)
def get_inspections(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(InspectionResult)

    if status and status.upper() != "ALL":
        query = query.filter(InspectionResult.status == status.upper())

    if search:
        query = query.filter(
            or_(
                InspectionResult.session_id.ilike(f"%{search}%"),
                InspectionResult.notes.ilike(f"%{search}%"),
                InspectionResult.source.ilike(f"%{search}%")
            )
        )

    results = query.order_by(InspectionResult.id.desc()).all()

    return {
        "total": len(results),
        "items": results
    }


@app.get("/inspection-results/{inspection_id}", response_model=InspectionResponse)
def get_inspection_detail(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(InspectionResult).filter(InspectionResult.id == inspection_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Inspection result not found")

    return result


# =========================
# SETTINGS
# =========================

@app.get("/settings", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = ensure_default_settings(db)
    return settings


@app.put("/settings", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = ensure_default_settings(db)

    if payload.live_camera is not None:
        settings.live_camera = payload.live_camera
    if payload.auto_save is not None:
        settings.auto_save = payload.auto_save
    if payload.ng_notification is not None:
        settings.ng_notification = payload.ng_notification
    if payload.sound_alert is not None:
        settings.sound_alert = payload.sound_alert

    db.commit()
    db.refresh(settings)

    logger.info("Settings updated")
    return settings


# =========================
# EXPORT
# =========================

@app.get("/export/csv")
def export_inspections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_path = f"exports/inspection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    results = db.query(InspectionResult).order_by(InspectionResult.id.desc()).all()

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id",
            "session_id",
            "length_mm",
            "width_mm",
            "status",
            "source",
            "notes",
            "image_path",
            "timestamp"
        ])

        for result in results:
            writer.writerow([
                result.id,
                result.session_id,
                result.length_mm,
                result.width_mm,
                result.status,
                result.source,
                result.notes,
                result.image_path,
                result.timestamp
            ])

    logger.info(f"Export created: {file_path}")
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="text/csv"
    )