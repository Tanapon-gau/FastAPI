# FastAPI Learning Project

โปรเจกต์นี้สร้างขึ้นเพื่อเรียนรู้การพัฒนา REST API แบบครบวงจร ตั้งแต่ local development จนถึง production deployment โดยใช้ Claude Code เป็น assistant ตลอดกระบวนการ

---

## สิ่งที่เรียนรู้

### 1. Backend Development
- **FastAPI** — สร้าง REST API, routing, Pydantic schema validation
- **SQLAlchemy** — ORM, database session management, Dependency Injection
- **JWT Authentication** — register, login, token verification ด้วย python-jose + passlib

### 2. Database
- **PostgreSQL** — relational database หลักของโปรเจกต์
- **Alembic** — database migration tool สำหรับ alter table โดยข้อมูลไม่หาย

### 3. Infrastructure
- **Docker + Docker Compose** — containerize API และ PostgreSQL
- **Environment Variables** — จัดการ config ด้วย `.env` และ `python-dotenv`

### 4. Code Quality
- **Ruff** — code formatter และ linter
- **Pylance** — static type checking, type hints ทุก function

### 5. Testing
- **pytest + httpx** — unit testing ด้วย `TestClient`
- **MagicMock** — mock database โดยไม่ต้องต่อ DB จริง
- **pytest-cov** — coverage report (95%+)

### 6. CI/CD
- **GitHub Actions** — แยก CI และ CD เป็นคนละ workflow
- **Render** — production deployment พร้อม deploy hook
- **Environment Protection** — require approval ก่อน deploy

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
│       └── cd.yml           # deploy to Render (main only)
│
├── .env.example             # template env variables
├── Dockerfile
├── docker-compose.yml
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

---

## CI/CD Flow

```
push to dev   →  CI: format → test + coverage 95%
push to main  →  CI: format → test + coverage 95%
                     ↓ (ถ้าผ่าน)
                 CD: รอ Approve → deploy to Render
```

---

## Security Notes

repo นี้เป็น public — สิ่งที่ sensitive ทั้งหมดถูกป้องกันดังนี้:

| ข้อมูล | วิธีป้องกัน |
|--------|------------|
| `DATABASE_URL`, `SECRET_KEY` | อยู่ใน `.env` ซึ่งอยู่ใน `.gitignore` ไม่ถูก push |
| `RENDER_DEPLOY_HOOK` | อยู่ใน GitHub Secret ค่าจริงไม่เคย expose ใน code |
| `.env.example` | มีแค่ชื่อ key ไม่มี value |

> **หมายเหตุ:** ถ้ามีคนรู้ Render Deploy Hook URL จะทำได้แค่ trigger redeploy code เดิม ไม่สามารถแก้ไขหรือเข้าถึงข้อมูลได้

---

## Commit Convention

โปรเจกต์นี้ใช้ [Conventional Commits](https://www.conventionalcommits.org)

| Prefix | ความหมาย |
|--------|----------|
| `feat` | เพิ่ม feature ใหม่ |
| `fix` | แก้ bug |
| `chore` | งาน maintenance ที่ไม่กระทบ logic เช่น update dependencies |
| `docs` | แก้ documentation |
| `refactor` | ปรับโค้ดโดยไม่เปลี่ยน behavior |
| `test` | เพิ่มหรือแก้ test |
| `ci` | แก้ CI/CD config |
| `style` | แก้ formatting ไม่กระทบ logic |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.128.8 |
| ORM | SQLAlchemy 2.0.49 |
| Database | PostgreSQL |
| Migration | Alembic 1.13.1 |
| Auth | python-jose + passlib + bcrypt |
| Testing | pytest + httpx + pytest-cov |
| Linter | Ruff |
| Deploy | Render (free tier) |
