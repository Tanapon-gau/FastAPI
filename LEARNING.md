# Learning Journal — FastAPI + PostgreSQL + Docker

## What I Built
A REST API with user authentication, built from scratch using
FastAPI, PostgreSQL, and Docker. The project covers the full
development workflow from local setup to a production-ready structure.

## Session 1 What I Learned

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

---

## Problems I Encountered and How I Solved Them

### uvicorn: command not found
- Cause: pip installed uvicorn in user-level Python path
  which was not in the shell PATH
- Fix: Added ~/Library/Python/3.9/bin to ~/.zshrc

### psycopg2.OperationalError on startup
- Cause: API container tried to connect to PostgreSQL
  before it was ready to accept connections
- Fix: Added healthcheck with pg_isready to docker-compose.yml
  and changed depends_on to wait for service_healthy

### column users.email does not exist
- Cause: Added new columns to models.py but SQLAlchemy's create_all()
  does not modify existing tables
- Fix: Ran docker compose down -v to drop the volume
  and recreate the database from scratch
- Long-term fix: Use Alembic for safe schema migrations

### ModuleNotFoundError: No module named 'jose'
- Cause: Library was installed in local venv but not inside the Docker container
- Fix: Added python-jose to requirements.txt and rebuilt the image

### bcrypt ValueError: password cannot be longer than 72 bytes
- Cause: bcrypt 5.0.0 is not fully compatible with passlib 1.7.4
- Fix: Pinned bcrypt to 4.0.1 in requirements.txt

### Pylance type errors
- Cause: SQLAlchemy columns return Column[str] not str,
  and os.getenv() returns str | None not str
- Fix: Wrapped SQLAlchemy values with str() or int(),
  and added default values to all os.getenv() calls

---

## Next Steps
- Dependency injection for cleaner session management
- Deploy to production

---

## Session 2 — Refactor, Testing, Alembic

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
- constructor คือ `__init__` ของ class รับ argument เหมือน function ปกติ

### Library Compatibility
- `passlib 1.7.4` ไม่รองรับ `bcrypt >= 4.0` ต้องใช้ `bcrypt==3.2.2`
- version ใน `requirements.txt` ต้องรองรับ Python version ที่ใช้ pytest 9.x รองรับ Python 3.10+ เท่านั้น Python 3.9 ต้องใช้ `pytest==8.4.2` (version สูงสุดที่รองรับ)

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
- Django มี `makemigrations` / `migrate` built-in ทำให้อัตโนมัติ
  FastAPI ต้อง setup Alembic เอง แต่ได้ความยืดหยุ่นมากกว่า

### Dependency Injection — Session Management
- `SessionLocal()` แบบเดิมต้องเปิด/ปิด session เองทุก route — ถ้า error กลางทางก่อนถึง `db.close()` session จะค้างไม่ถูกปิด
- Session ที่ค้างอยู่คือ connection ที่ถูกจองไว้ PostgreSQL มี connection จำกัด (default 100)
  ถ้าค้างมากพอจะเกิด `too many connections` — มักไม่เจอตอน dev แต่พังตอน production ที่มี traffic จริง
- แก้ด้วย `get_db()` generator + `Depends`:
  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db      # ส่ง session ให้ route ใช้
      finally:
          db.close()    # ปิดเสมอ แม้จะ error

  def register(user: UserCreate, db: Session = Depends(get_db)):
      # ได้ db มาพร้อมใช้ ไม่ต้องเปิด/ปิดเอง
  ```
- `yield` แบ่ง function เป็นสองช่วง — ก่อนและหลัง route รัน FastAPI จัดการ lifecycle ให้เอง
- concept นี้ใช้กับทุก database (MySQL, MongoDB, Redis) และทุก resource ที่มีจำนวนจำกัด เช่น file handle, HTTP connection, network socket
- ใน test ใช้ `app.dependency_overrides[get_db] = lambda: mock_db` แทน `@patch` เพราะ FastAPI ออกแบบมาให้ override dependency ตอน test โดยเฉพาะ

### CI/CD — GitHub Actions
- workflow แบ่งเป็น 3 jobs: `format` → `test` → `deploy` (รันตามลำดับด้วย `needs`)
- `deploy` job รันเฉพาะตอน push ไป `main` เท่านั้น ไม่รันตอน PR
- Secret ที่อยู่ใน **Environment** ต้องระบุ `environment: <ชื่อ>` ใน job ด้วย ไม่งั้นอ่านค่าไม่ได้
- `HTTPBearer` คืน status code ต่างกันตาม FastAPI version — ควร pin version ใน `requirements.txt` ให้ตรงกับที่ test บน local เสมอ

### GitHub Actions — action versioning
- syntax `uses: actions/checkout@v6` คือ owner/repo@version เป็น syntax เฉพาะของ GitHub Actions
- สิ่งที่ใส่หลัง `@` ได้:
  ```yaml
  actions/checkout@v6        # major version (แนะนำ)
  actions/checkout@v6.0.2    # exact version
  actions/checkout@main      # branch (ไม่ stable)
  actions/checkout@sha       # commit SHA (ปลอดภัยที่สุด)
  ```
- Node.js version ของ action runner ไม่กระทบ Python code เลย — แค่ต้องอัปเดต action version ให้รองรับ Node version ใหม่
- ดู version ล่าสุดได้ที่ github.com/marketplace หรือ github.com/actions/&lt;action-name&gt;/releases