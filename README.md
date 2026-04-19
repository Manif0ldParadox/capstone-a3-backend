# Automated Inspection Backend API

Backend API untuk sistem **Automated Dimensional Inspection** berbasis **FastAPI**.  
Backend ini menangani autentikasi user, dashboard summary, sesi inspeksi, penyimpanan hasil inspeksi, history, settings, dan export laporan CSV.

---

## Tech Stack

- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- JWT Authentication
- Passlib bcrypt
- Python Dotenv

---

## Project Structure

```bash
capstone-a3/
├── main.py
├── auth.py
├── database.py
├── models.py
├── schemas.py
├── .env.example
├── requirements.txt
├── inspection.db
├── logs/
└── exports/

## Dummy Accounts

Supervisor:
- email: supervisor@example.com
- password: supervisor123

Operator:
- email: operator@example.com
- password: operator123
