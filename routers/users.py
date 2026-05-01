from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth import create_access_token, hash_password, verify_password, verify_token
from database import get_db
from models import User
from schemas import LoginRequest, Token, UserCreate, UserResponse

router = APIRouter()
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    payload: Optional[dict] = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้อง")
    return payload


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)) -> User:
    existing: Optional[User] = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email นี้มีแล้ว")
    new_user = User(
        name=user.name, email=user.email, password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user: Optional[User] = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, str(user.password)):
        raise HTTPException(status_code=401, detail="Email หรือ password ไม่ถูกต้อง")
    token = create_access_token({"sub": str(user.email)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> list:
    return db.query(User).all()
