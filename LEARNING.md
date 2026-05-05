# Learning Journal — FastAPI Project

โปรเจกต์นี้บันทึกสิ่งที่เรียนรู้จากการสร้าง REST API ด้วย FastAPI ตั้งแต่ local development จนถึง production deployment

---

## สิ่งที่เรียนรู้ภาพรวม

### Backend
- **FastAPI** — REST API, routing, Pydantic schema validation
- **SQLAlchemy** — ORM, database session management, Dependency Injection
- **JWT Authentication** — register, login, token verification ด้วย python-jose + passlib

### Database
- **PostgreSQL** — relational database หลักของโปรเจกต์
- **Alembic** — database migration tool สำหรับ alter table โดยข้อมูลไม่หาย
- **Neon** — serverless PostgreSQL, scale to zero, รองรับ PostgreSQL 18
- **Internal vs External URL** — Internal สำหรับ app บน Render, External สำหรับ tools ภายนอก

### Infrastructure
- **Docker + Docker Compose** — containerize API และ PostgreSQL
- **Environment Variables** — จัดการ config ด้วย `.env` และ `python-dotenv`
- **Render** — web service deployment, free plan ข้อจำกัด

### Code Quality
- **Ruff** — code formatter และ linter แทน Black + Flake8
- **Pylance** — static type checking, type hints ทุก function
- **CI as gatekeeper** — `ruff format --check` บังคับ format ก่อน merge

### Testing
- **pytest + httpx** — unit testing ด้วย `TestClient`
- **MagicMock** — mock database โดยไม่ต้องต่อ DB จริง
- **pytest-cov** — coverage report (95%+)

### CI/CD
- **GitHub Actions** — แยก CI และ CD เป็นคนละ workflow
- **CI** — ตรวจสอบความถูกต้องของโค้ด: format, lint, test, coverage
- **CD** — นำโค้ดที่ผ่าน CI ไปขึ้น environment จริง: migrate, deploy
- **Repository vs Environment secrets** — เข้าถึง secret ต่างกันตาม job

---

## Session 1 — FastAPI, SQLAlchemy, Docker, Auth

### FastAPI
- How to create API routes using decorators (@app.get, @app.post, etc.)
- How path parameters work e.g. /users/{id}
- How FastAPI automatically generates interactive docs at /docs
- How Depends() works for dependency injection
- How Pydantic schemas validate incoming and outgoing data

### SQLAlchemy
- How to define database tables as Python classes using ORM
- How to open and close sessions to query the database
- How filter() works as the equivalent of SQL WHERE
- Why create_all() only creates tables and never modifies existing ones
- The difference between models (database shape) and schemas (API shape)

### Docker
- What Docker images and containers are and how they relate
- How to write a Dockerfile to containerize a Python application
- How docker-compose.yml manages multiple services together
- Why COPY requirements.txt before COPY . . speeds up builds using layer caching
- Why volumes are useful in development but should never be used in production
- How healthcheck ensures PostgreSQL is ready before the API starts

### Authentication
- How JWT works: header, payload, and signature
- Why passwords must be hashed before storing in the database
- Why bcrypt is preferred over MD5 or SHA256 for password hashing
- How passlib wraps bcrypt so we don't interact with it directly
- How OAuth2PasswordBearer protects routes in FastAPI

### Python Best Practices
- Why virtual environments (venv) are essential when working on multiple projects
- Why requirements.txt should pin exact versions to ensure consistency
- How to use os.getenv() with a default value to avoid None errors
- How to write Pylance-compatible code with proper type hints

### Project Structure
- Why splitting files by responsibility makes the codebase easier to maintain
- How routers let you group related routes into separate files
- Why .env files should never be committed to git
- How .env.example communicates required config without exposing secrets

### Problems

**uvicorn: command not found**
- Cause: pip installed uvicorn in user-level Python path which was not in the shell PATH
- Fix: Added ~/Library/Python/3.9/bin to ~/.zshrc

**psycopg2.OperationalError on startup**
- Cause: API container tried to connect to PostgreSQL before it was ready
- Fix: Added healthcheck with pg_isready to docker-compose.yml and changed depends_on to wait for service_healthy

**column users.email does not exist**
- Cause: Added new columns to models.py but SQLAlchemy's create_all() does not modify existing tables
- Fix: Ran docker compose down -v to recreate the database from scratch
- Long-term fix: Use Alembic for safe schema migrations

**ModuleNotFoundError: No module named 'jose'**
- Cause: Library was installed in local venv but not inside the Docker container
- Fix: Added python-jose to requirements.txt and rebuilt the image

**bcrypt ValueError: password cannot be longer than 72 bytes**
- Cause: bcrypt 5.0.0 is not fully compatible with passlib 1.7.4
- Fix: Pinned bcrypt to 3.2.2 in requirements.txt

**Pylance type errors**
- Cause: SQLAlchemy columns return Column[str] not str, and os.getenv() returns str | None not str
- Fix: Wrapped SQLAlchemy values with str() or int(), and added default values to all os.getenv() calls

---

## Session 2 — Refactor, Testing, Alembic, CI/CD

### File Structure
- `models.py` ต้อง import `Base` จาก `database.py` เสมอ ห้ามสร้างแยก
  เพราะ Alembic ดึง `Base` จาก `database.py` — ถ้าแยก Alembic จะไม่รู้จัก model
  และ autogenerate จะคิดว่า table ควรถูกลบ

### venv vs Docker
- venv และ Docker container เป็น Python environment แยกกันสนิท ไม่ sync กัน
- `volumes: .:/app` mount แค่ code ไม่ใช่ library
- เปลี่ยน requirements.txt แล้วต้อง `docker-compose build` ใหม่เสมอ

### Swagger / Authentication
- `OAuth2PasswordBearer` ทำให้ Swagger แสดง username/password form
  แต่ถ้า `/login` รับ JSON ให้ใช้ `HTTPBearer` แทน — Swagger จะแสดง text field ให้วาง token ได้โดยตรง

### Unit Testing
- ใช้ `pytest` + `httpx` + `TestClient` จาก FastAPI
- Mock database ด้วย `unittest.mock.MagicMock` ไม่ต้องต่อ DB จริง
- สร้าง `tests/conftest.py` set `DATABASE_URL=sqlite:///:memory:` ก่อน import app
  เพราะ `main.py` เรียก `create_all` ตอน import ซึ่งจะพยายามต่อ DB ทันที
- สร้าง model object ด้วย constructor ไม่ใช่ assign ทีละ attribute
  ```python
  # ถูก — Pylance ไม่ complain
  user = User(id=1, name="test", email="a@b.com")

  # ผิด — Pylance มอง id เป็น Column[int] ไม่ใช่ int
  user = User()
  user.id = 1
  ```

### Library Compatibility
- `passlib 1.7.4` ไม่รองรับ `bcrypt >= 4.0` ต้องใช้ `bcrypt==3.2.2`
- pytest 9.x รองรับ Python 3.10+ เท่านั้น Python 3.9 ต้องใช้ `pytest==8.4.2`

### Alembic
- `create_all()` สร้างแค่ table ใหม่ ไม่แตะ table ที่มีอยู่แล้ว
- Alembic track version และ autogenerate migration script จาก model ที่เปลี่ยน
  เช่น เพิ่ม column → `ALTER TABLE` ให้อัตโนมัติ โดยข้อมูลเดิมไม่หาย
- ต้องรันใน Docker container เพราะ hostname `db` มีแค่ใน Docker network
  ```bash
  docker exec <container> alembic revision --autogenerate -m "message"
  docker exec <container> alembic upgrade head
  docker exec <container> alembic downgrade -1
  ```
- Django มี `makemigrations` / `migrate` built-in — FastAPI ต้อง setup Alembic เอง แต่ได้ความยืดหยุ่นมากกว่า

### Dependency Injection — Session Management
- `SessionLocal()` แบบเดิมต้องเปิด/ปิด session เองทุก route — ถ้า error กลางทางก่อนถึง `db.close()` session จะค้างไม่ถูกปิด
- Session ที่ค้างอยู่คือ connection ที่ถูกจองไว้ PostgreSQL มี connection จำกัด (default 100)
  ถ้าค้างมากพอจะเกิด `too many connections` — มักไม่เจอตอน dev แต่พังตอน production
- แก้ด้วย `get_db()` generator + `Depends`:
  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db      # ส่ง session ให้ route ใช้
      finally:
          db.close()    # ปิดเสมอ แม้จะ error
  ```
- ใน test ใช้ `app.dependency_overrides[get_db] = lambda: mock_db` แทน `@patch`

### CI/CD — GitHub Actions
- workflow แบ่งเป็น 3 jobs: `format` → `test` → `deploy`
- Secret ที่อยู่ใน **Environment** ต้องระบุ `environment: <ชื่อ>` ใน job ด้วย ไม่งั้นอ่านค่าไม่ได้
- `HTTPBearer` คืน status code ต่างกันตาม FastAPI version — ควร pin version ใน `requirements.txt`

### GitHub Actions — action versioning
- syntax `uses: actions/checkout@v6` คือ owner/repo@version
- สิ่งที่ใส่หลัง `@` ได้:
  ```yaml
  actions/checkout@v6        # major version (แนะนำ)
  actions/checkout@v6.0.2    # exact version
  actions/checkout@main      # branch (ไม่ stable)
  actions/checkout@sha       # commit SHA (ปลอดภัยที่สุด)
  ```

---

## Session 3 — Database Connection, Deployment, Neon

### Render Internal vs External URL
- Internal hostname (`dpg-xxx`) ใช้ได้เฉพาะใน Render private network — DBeaver บนเครื่องเข้าไม่ได้
- External hostname (`dpg-xxx.oregon-postgres.render.com`) ใช้สำหรับ tools ภายนอก
- App บน Render ใช้ Internal, DBeaver ใช้ External — credentials เหมือนกันทุกอย่างต่างแค่ host

### Individual DB env vars
- แยก `DATABASE_URL` เป็น `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- ทำให้เปลี่ยนแค่ `DB_HOST` เพื่อสลับระหว่าง Internal (app) และ External (DBeaver)
- ใช้ `or` แทน default parameter เพื่อรับมือกับ empty string:
  ```python
  DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql://{DB_USER}:..."
  ```
  เหตุผล: `os.getenv("KEY", default)` คืน default เฉพาะตอน KEY ไม่มีเลย แต่ถ้า KEY="" จะได้ "" แทน

### Render Free Plan ข้อจำกัด
- `preDeployCommand` ใช้ไม่ได้บน free plan
- SSH / Shell access ใช้ไม่ได้บน free plan
- ทั้งสองอย่างจำเป็นสำหรับรัน Alembic migration บน server
- แก้: ย้าย database ไปใช้ **Neon** และรัน migration ผ่าน **GitHub Actions CD** แทน
- บทเรียน: เช็ค feature ที่ต้องการก่อนเลือก platform โดยเฉพาะ free tier

### GitHub Actions Secrets — Repository vs Environment
- **Repository secrets**: เข้าถึงได้ทุก job โดยไม่ต้องระบุ `environment`
- **Environment secrets**: เข้าถึงได้เฉพาะ job ที่ระบุ `environment: <ชื่อ>` เท่านั้น
- ถ้าใส่ secret ผิดที่ → job อ่านค่าไม่ได้ → ได้ empty string → code ใช้ค่า default แทน
- `NEON_DATABASE_URL` → Repository secret (migrate job ไม่มี environment)
- `RENDER_DEPLOY_HOOK` → Environment secret (ต้องการ approval gate ก่อน deploy)

### Alembic autogenerate ออกมาเป็น `pass`
- เกิดเมื่อรัน `alembic revision --autogenerate` โดยที่ `alembic/env.py` ยังไม่มี `import models`
- Alembic ไม่รู้จัก model → คิดว่าไม่มีอะไรต้องสร้าง → `upgrade()` เป็น `pass`
- แก้: ต้องมี `import models` ใน `env.py` ก่อนรัน autogenerate เสมอ
- บทเรียน: หลัง autogenerate ให้เปิดไฟล์ migration ตรวจสอบว่า `upgrade()` มี SQL จริง ไม่ใช่แค่ `pass`

### Neon — Serverless PostgreSQL
- Database ทั่วไปรัน server ตลอด 24 ชั่วโมงและจ่ายเงินตลอดแม้ไม่มีคนใช้
- Neon เป็น **serverless** — database หยุดทำงานอัตโนมัติตอนไม่มี request (scale to zero)
  และตื่นขึ้นมาเองตอนมี connection (~500ms) จ่ายเงินเฉพาะตอนใช้งานจริง
- โค้ด Python ไม่ต้องเปลี่ยนอะไร — เปลี่ยนแค่ connection string
- ใช้ `sslmode=require` เสมอ: `postgresql://user:pass@host/db?sslmode=require`
- free tier รองรับ PostgreSQL 18, storage 0.5 GB
- migration รันผ่าน GitHub Actions CD โดย set `NEON_DATABASE_URL` เป็น Repository secret
- สถาปัตยกรรมของโปรเจกต์นี้:
  ```
  Render (web app) → เชื่อมต่อ → Neon (database)
  GitHub Actions   → รัน migration → Neon
  ```

### Scale to Zero คืออะไร
- Database **หยุดทำงานอัตโนมัติ** เมื่อไม่มี connection และ**ตื่นขึ้นมาเองเมื่อมี request**
- Free plan: หยุดหลังไม่มีใช้งาน 5 นาที, ตื่นใน ~500ms (cold start)
- นับ compute hours เฉพาะตอนที่ database ตื่นอยู่ — ไม่นับตอนหยุด
- Free plan ให้ 100 CU-hours/project/month (รีเซ็ตทุกเดือน)
  - ถ้าใช้หมดก่อนสิ้นเดือน → database suspend จนกว่าจะรีเซ็ต
  - default compute ของ free plan คือ 0.25 CU → active ได้ 400 ชั่วโมง/เดือน
  - สำหรับโปรเจกต์เรียนรู้ 100 CU-hours/เดือนเกินพอ

### Neon vs DynamoDB vs AWS RDS
เลือก database service ให้ตรงกับลักษณะงาน:

| | Neon | DynamoDB | AWS RDS |
|---|---|---|---|
| ประเภท | Relational (PostgreSQL) | NoSQL (Key-Value) | Relational (MySQL/PostgreSQL) |
| Query | SQL | PartiQL / SDK | SQL |
| Scale to zero | ✅ | ✅ | ❌ (ยกเว้น Aurora Serverless) |
| จ่ายตอนไม่ใช้ | ไม่จ่าย | ไม่จ่าย | จ่ายตลอด (per hour) |
| Free tier | ตลอดไป | ตลอดไป | 12 เดือนแรกเท่านั้น |

- **Neon** — เหมาะกับโปรเจกต์ที่ใช้ SQL, มี schema ชัดเจน, traffic ไม่สม่ำเสมอ
- **DynamoDB** — เหมาะกับ scale ใหญ่มาก, access pattern ชัด (lookup by key), ไม่ต้องการ JOIN, อยู่ใน AWS ecosystem
- **AWS RDS** — เหมาะกับ production จริงจัง ที่ต้องการ HA, automated backups, read replicas และยอมจ่าย server ตลอดเพื่อ performance ที่ stable

โปรเจกต์นี้ใช้ Neon เพราะ: ใช้ PostgreSQL เหมือนกันทุกอย่าง, free tier ตลอดไป, scale to zero ประหยัด CU-hours สำหรับ dev/learning

### Problems

**DBeaver: Unknown host (Internal hostname)**
- Cause: ใช้ Internal hostname (`dpg-xxx`) ซึ่งใช้ได้แค่ใน Render network
- Fix: เปลี่ยนเป็น External hostname (`dpg-xxx.oregon-postgres.render.com`)

**DBeaver: Invalid JDBC URL**
- Cause: URL ขาด port `:5432`
- Fix: กรอก individual fields (Host/Port/Database/Username/Password) แทนการ paste URL

**CI fail: ruff format check**
- Cause: แก้โค้ดแล้วลืมรัน `ruff format .` ก่อน commit
- Fix: รัน `venv/bin/ruff format .` ก่อน commit ทุกครั้ง
- Note: CI ไม่มี venv — ruff ติดตั้งตรงๆ ผ่าน pip ไม่ต้อง activate venv

**GitHub Actions secret ไม่ถูกอ่าน**
- Cause: เพิ่ม secret ใน Environment (Main) แทน Repository secrets
- Fix: ย้าย `NEON_DATABASE_URL` ไปที่ Repository secrets

**Alembic migration ไม่สร้าง table**
- Cause: migration แรกเป็น `pass` เพราะ `import models` ยังไม่มีตอน autogenerate
- Fix: เพิ่ม `upgrade()` ใน migration แรกให้ตรงกับ model จริง
