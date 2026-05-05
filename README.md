# FastAPI Learning Project

โปรเจกต์นี้สร้างขึ้นเพื่อเรียนรู้การพัฒนา REST API แบบครบวงจร ตั้งแต่ local development จนถึง production deployment โดยใช้ Claude Code เป็น assistant ตลอดกระบวนการ

---

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.128.8 |
| ORM | SQLAlchemy 2.0.49 |
| Database | PostgreSQL 18 (Neon) |
| Migration | Alembic 1.13.1 |
| Auth | python-jose + passlib + bcrypt |
| Testing | pytest + httpx + pytest-cov |
| Linter | Ruff |
| Deploy | Render (web) + Neon (database) |

---

## Project Structure

```
FastAPI/
├── main.py                  # app entry point
├── database.py              # engine, session, get_db()
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic request/response schemas
├── auth.py                  # JWT, password hashing
│
├── routers/
│   └── users.py             # register, login, GET /users
│
├── alembic/                 # database migrations
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── conftest.py          # SQLite in-memory สำหรับ test
│   ├── test_auth.py         # unit tests สำหรับ auth functions
│   └── test_users.py        # unit tests สำหรับ API routes
│
├── .github/
│   └── workflows/
│       ├── ci.yml           # format + test + coverage (dev & main)
│       └── cd.yml           # migrate + deploy to Render (main only)
│
├── .env.example             # template env variables
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
└── ruff.toml
```

---

## API Routes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | — | API info และวิธีใช้ |
| POST | `/register` | — | สร้าง account ใหม่ |
| POST | `/login` | — | รับ JWT token |
| GET | `/users` | Bearer token | ดึงข้อมูล users ทั้งหมด |

---

## การใช้งาน

### Local (Docker)

```bash
# รัน API + PostgreSQL
docker-compose up

# รัน migration
docker exec <container> alembic upgrade head
```

### ทดสอบผ่าน Swagger UI

1. เปิด `http://localhost:8000/docs`
2. POST `/register` — สร้าง account
3. POST `/login` — copy `access_token`
4. กด **Authorize** → วาง token
5. GET `/users`

### รัน Tests

```bash
pytest tests/ -v --cov=. --cov-report=term-missing --ignore=venv
```

### Ruff (ควรรันก่อน commit ทุกครั้ง)

```bash
venv/bin/ruff format .
venv/bin/ruff check .
```

---

## CI/CD Flow

```
push to dev   →  CI: format → test + coverage 95%
push to main  →  CI: format → test + coverage 95%
                     ↓ (ถ้าผ่าน)
                 CD: migrate (Neon) → รอ Approve → deploy to Render
```

### ลำดับที่ควรทำก่อน deploy

1. **รัน migration ใน local** — ทดสอบว่า migration ใช้งานได้กับ database local ก่อน
   ถ้าผ่านใน local แสดงว่า migration ถูกต้อง prod ก็ควรผ่านเช่นกัน
2. **รัน tests** — ตรวจสอบว่าโค้ดไม่พัง
3. **push to main** — CI/CD จะรัน migration บน Neon แล้ว deploy ไป Render อัตโนมัติ

> สำหรับโปรเจกต์ขนาดใหญ่ควรทำตามลำดับนี้เสมอ เพราะ migration ที่พังบน production อาจทำให้ระบบหยุดทำงานทั้งหมด

---

## Security Notes

repo นี้เป็น public — สิ่งที่ sensitive ทั้งหมดถูกป้องกันดังนี้:

| ข้อมูล | วิธีป้องกัน |
|--------|------------|
| `DB_*`, `SECRET_KEY` | อยู่ใน `.env` ซึ่งอยู่ใน `.gitignore` ไม่ถูก push |
| `NEON_DATABASE_URL` | อยู่ใน GitHub Repository Secret |
| `RENDER_DEPLOY_HOOK` | อยู่ใน GitHub Environment Secret (Main) |
| `.env.example` | มีแค่ชื่อ key ไม่มี value |

---

## Commit Convention

โปรเจกต์นี้ใช้ [Conventional Commits](https://www.conventionalcommits.org)

| Prefix | ความหมาย |
|--------|----------|
| `feat` | เพิ่ม feature ใหม่ |
| `fix` | แก้ bug |
| `chore` | งาน maintenance ที่ไม่กระทบ logic |
| `docs` | แก้ documentation |
| `refactor` | ปรับโค้ดโดยไม่เปลี่ยน behavior |
| `test` | เพิ่มหรือแก้ test |
| `ci` | แก้ CI/CD config |
| `style` | แก้ formatting ไม่กระทบ logic |
