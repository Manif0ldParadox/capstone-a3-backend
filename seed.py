from database import SessionLocal, engine, Base
from models import User, InspectionSession, InspectionResult, SystemSettings
from auth import hash_password


def seed_data():
    db = SessionLocal()

    try:
        # Buat tabel kalau belum ada
        Base.metadata.create_all(bind=engine)

        # =========================
        # SEED USERS
        # =========================
        existing_supervisor = db.query(User).filter(User.email == "supervisor@example.com").first()
        if not existing_supervisor:
            supervisor = User(
                full_name="Supervisor QC",
                email="supervisor@example.com",
                password_hash=hash_password("supervisor123"),
                role="supervisor"
            )
            db.add(supervisor)
            print("Supervisor user created")
        else:
            print("Supervisor user already exists")

        existing_operator = db.query(User).filter(User.email == "operator@example.com").first()
        if not existing_operator:
            operator = User(
                full_name="Operator QC",
                email="operator@example.com",
                password_hash=hash_password("operator123"),
                role="operator"
            )
            db.add(operator)
            print("Operator user created")
        else:
            print("Operator user already exists")

        db.commit()

        # =========================
        # SEED SETTINGS
        # =========================
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
            print("Default system settings created")
        else:
            print("System settings already exist")

        # =========================
        # SEED INSPECTION SESSION
        # =========================
        existing_session = db.query(InspectionSession).filter(
            InspectionSession.session_id == "S000001"
        ).first()

        if not existing_session:
            session = InspectionSession(
                session_id="S000001",
                source="Camera 1",
                status="active"
            )
            db.add(session)
            db.commit()
            print("Inspection session created")
        else:
            print("Inspection session already exists")

        # =========================
        # SEED INSPECTION RESULTS
        # =========================
        existing_result_1 = db.query(InspectionResult).filter(
            InspectionResult.session_id == "S000001",
            InspectionResult.status == "OK"
        ).first()

        if not existing_result_1:
            result_ok = InspectionResult(
                session_id="S000001",
                length_mm=32.5,
                width_mm=12.4,
                status="OK",
                source="Camera 1",
                notes="within tolerance",
                image_path="captures/sample.jpg"
            )
            db.add(result_ok)
            db.commit()
            print("OK inspection result created")
        else:
            print("OK inspection result already exists")

        existing_result_2 = db.query(InspectionResult).filter(
            InspectionResult.session_id == "S000001",
            InspectionResult.status == "NG"
        ).first()

        if not existing_result_2:
            result_ng = InspectionResult(
                session_id="S000001",
                length_mm=35.9,
                width_mm=12.4,
                status="NG",
                source="Camera 1",
                notes="length exceeds tolerance",
                image_path="captures/sample_ng.jpg"
            )
            db.add(result_ng)
            db.commit()
            print("NG inspection result created")
        else:
            print("NG inspection result already exists")

        print("Seeding completed successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()