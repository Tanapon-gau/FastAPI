from fastapi import FastAPI

from routers import users

app = FastAPI()

app.include_router(users.router)


@app.get("/")
def hello() -> dict:
    return {
        "message": "FastAPI is running",
        "docs": "/docs",
        "how_to_use": [
            "1. POST /register — สร้าง account ใหม่",
            "2. POST /login — รับ access_token",
            "3. ไปที่ /docs กด Authorize แล้ววาง token",
            "4. GET /users — ดึงข้อมูล users ทั้งหมด",
        ],
    }
