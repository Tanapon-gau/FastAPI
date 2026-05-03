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
- **Internal vs External URL** — แยกใช้งานตาม context: Internal สำหรับ app บน Render, External สำหรับ tools ภายนอก
- **Individual DB env vars** — แยก host/port/user/password เป็น vars อิสระ แทนการใช้ connection string เดียว

### 3. Infrastructure
- **Docker + Docker Compose** — containerize API และ PostgreSQL
- **Environment Variables** — จัดการ config ด้วย `.env` และ `python-dotenv`
- **Render Deployment** — pre-deploy command, connection limits, storage autoscaling

### 4. Code Quality
- **Ruff** — code formatter และ linter แทน Black + Flake8
- **Pylance** — static type checking, type hints ทุก function
- **CI** — ใช้ `ruff format --check` ใน CI เพื่อบังคับ format ก่อน merge

### 5. Testing
- **pytest + httpx** — unit testing ด้วย `TestClient`
- **MagicMock** — mock database โดยไม่ต้องต่อ DB จริง
- **pytest-cov** — coverage report (95%+)

### 6. CI/CD
- **GitHub Actions** — แยก CI และ CD เป็นคนละ workflow
- **Render** — production deployment พร้อม deploy hook
- **Environment Protection** — require approval ก่อน deploy
- **CI หน้าที่** — ตรวจสอบความถูกต้องของโค้ด: format, lint, type check, test, coverage, build
- **CD หน้าที่** — นำโค้ดที่ผ่าน CI ไปขึ้น environment จริง: deploy, migration, notify, rollback
- **ความแตกต่าง** — CI ถามว่า "โค้ดถูกไหม?" CD ถามว่า "ขึ้น production ได้ไหม?"

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

### Ruff (ควรรันก่อน commit ทุกครั้ง)

```bash
# format โค้ดทุกไฟล์
venv/bin/ruff format .

# เช็ค lint
venv/bin/ruff check .
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

## LEARNING — ปัญหาที่เจอและวิธีแก้

### 1. เช็คว่า Alembic รันบน Render แล้วหรือยัง

**ปัญหา:** ไม่รู้ว่า pre-deploy command (`alembic upgrade head`) รันสำเร็จจริงหรือเปล่า

**สาเหตุ:** Render แยก pre-deploy step ออกจาก deploy log ทั่วไป ทำให้หาไม่เจอถ้าไม่รู้ว่าต้องดูที่ไหน

**วิธีแก้:** มี 3 ทาง
- Render Dashboard → Deploys → เลือก deploy → ดู section **"Pre-deploy"** จะเห็น output ของ alembic โดยตรง
- Query ตาราง `alembic_version` ใน database ตรงๆ — Alembic สร้างตารางนี้ไว้เสมอ
- เข้า Render Shell แล้วรัน `alembic current` เพื่อดู revision ปัจจุบัน (Plan Free ใช้ไม่ได้)

---

### 2. DBeaver เชื่อมต่อ DB ไม่ได้: Unknown host

**ปัญหา:** DBeaver ขึ้น `The connection attempt failed. Unknown host dpg-d7rl68egvqtc73bj61p0-a`

**สาเหตุ:** `dpg-d7rl68egvqtc73bj61p0-a` คือ **Internal hostname** ที่ Render ใช้ภายใน private network เท่านั้น เครื่องภายนอกอย่าง DBeaver ไม่สามารถ resolve ได้

**วิธีแก้:** ใช้ **External hostname** จาก Render Dashboard แทน ซึ่งมีรูปแบบ:
```
dpg-d7rl68egvqtc73bj61p0-a.oregon-postgres.render.com
```
> หลักการ: Internal URL ใช้สำหรับ app บน Render เท่านั้น, External URL ใช้สำหรับ tools ภายนอก

---

### 3. DBeaver ขึ้น Invalid JDBC URL

**ปัญหา:** paste connection string แล้วขึ้น `Invalid JDBC URL`

**สาเหตุ:** URL ขาด port `:5432` ทำให้ JDBC driver parse ไม่ได้

**วิธีแก้:** เพิ่ม `:5432` ให้ครบ หรือกรอก **individual fields** (Host / Port / Database / Username / Password) แทนการ paste URL ตรงๆ จะไม่มีปัญหา format

---

### 4. แยก env vars แทน DATABASE_URL เดียว

**ปัญหา:** ใช้ `DATABASE_URL` เป็น string เดียว ทำให้ยากต่อการเชื่อมต่อจาก tools ภายนอก เพราะต้องรู้ format URL ทั้งหมด

**สาเหตุ:** Connection string แบบ URL มี Internal/External hostname ต่างกัน แต่ user/password/port/dbname เหมือนกัน การแยก vars ทำให้เปลี่ยนแค่ `DB_HOST` ได้โดยไม่ต้องสร้าง URL ใหม่ทั้งหมด

**วิธีแก้:** แยก env vars เป็น `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` แล้วให้ Python ประกอบ URL เอง:
```python
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```
ผลคือ DBeaver กับ app ใช้ค่า field เดียวกันทุกอย่าง ต่างแค่ `DB_HOST`

---

### 6. CI vs CD ต่างกันอย่างไร

**ปัญหา:** สับสนว่า CI กับ CD ทำหน้าที่อะไร และแบ่งงานกันยังไง

**สาเหตุ:** ชื่อ "CI/CD" มักถูกพูดรวมกัน ทำให้เข้าใจว่าเป็นสิ่งเดียวกัน

**วิธีแก้/สิ่งที่เรียน:**

| | CI (Continuous Integration) | CD (Continuous Delivery/Deployment) |
|--|----------------------------|--------------------------------------|
| ถามว่า | โค้ดนี้ถูกต้องไหม? | โค้ดนี้ขึ้น production ได้ไหม? |
| Trigger | ทุก push / PR | เฉพาะ branch หลัก (main) |
| ถ้า fail | ห้าม merge | ห้าม deploy |

**CI ทำอะไรบ้าง:**
- Format / Lint — ruff, eslint
- Type check — mypy, pyright
- Unit / Integration tests — pytest, jest
- Coverage threshold — บังคับว่าต้องมี test กี่ %
- Security scan — ตรวจ dependency ที่มีช่องโหว่
- Build — ตรวจว่า Docker build หรือ npm build ผ่าน

**CD ทำอะไรบ้าง:**
- Deploy to staging — ขึ้น environment ทดสอบก่อน
- Run migration — `alembic upgrade head` ก่อน app ขึ้น (pre-deploy)
- Deploy to production — ขึ้น server จริง
- Notify — แจ้ง Slack / Teams ว่า deploy สำเร็จหรือ fail
- Rollback — ถ้า deploy แล้วพังให้ย้อนกลับ version เดิม

> โปรเจกต์นี้: CI เช็ค format + test + coverage, CD รอ approve แล้ว deploy ไป Render พร้อม pre-deploy alembic

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
