# Project Context — FastAPI + PostgreSQL + Docker

## Completed
- FastAPI + PostgreSQL + Docker compose
- File structure: database.py, models.py, schemas.py, routers/users.py
- JWT Authentication (python-jose + passlib + bcrypt==4.0.1)
- Environment variables via .env
- requirements.txt with pinned versions
- Full Pylance type hint support

## Project Structure
myproject/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── routers/
│   ├── __init__.py
│   └── users.py
├── tests/
│   ├── __init__.py
│   └── test_users.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

## Stack
- FastAPI 0.128.8
- SQLAlchemy 2.0.49
- PostgreSQL (Docker image)
- python-jose 3.5.0
- passlib 1.7.4
- bcrypt 4.0.1
- uvicorn 0.39.0
- pytest + httpx for unit testing

## API Routes
- POST /register — create new user
- POST /login — get JWT token
- GET /users — get all users (requires token)
- PUT /users/{id} — update user (requires token)
- DELETE /users/{id} — delete user (requires token)

## Coding Standards
- Full Pylance support on all files
- Every function must have a return type
- Variables that may be None must use Optional[type]
- SQLAlchemy columns passed to functions must be wrapped with str() or int()
- os.getenv() must always have a default value

## Unit Testing
- Using pytest + httpx
- Test database is separate from production, uses SQLite during testing
- Every route must have test coverage
- Required test cases
  - register success
  - register duplicate email
  - login success
  - login wrong password
  - GET /users with valid token
  - GET /users without token must return 401

## Next Steps
- Unit testing
- Alembic for database migration
- Dependency Injection for session management
- Deploy to production server