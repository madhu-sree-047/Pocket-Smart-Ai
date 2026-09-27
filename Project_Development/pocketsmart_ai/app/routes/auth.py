from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.db import User
from app.models.schemas import SessionInfo, Token, UserCreate, UserLogin
from app.dependencies import get_current_user

router=APIRouter(tags=["auth"])

def _token_response(response: Response, user: User):
    token=create_access_token(str(user.id)); response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=3600)
    return Token(access_token=token)

@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, response: Response, db: Session=Depends(get_db)):
    if db.scalar(select(User).where(User.email==payload.email.lower())):
        raise HTTPException(409,"Email already registered")
    user=User(name=payload.name.strip(), email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return _token_response(response,user)

@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, db: Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower()))
    if not user or not verify_password(payload.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Invalid email or password")
    return _token_response(response,user)

@router.post("/token", response_model=Token)
def token(payload: UserLogin, response: Response, db: Session=Depends(get_db)):
    return login(payload,response,db)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message":"Logged out"}

@router.get("/session-info", response_model=SessionInfo)
def session_info(request: Request, db: Session=Depends(get_db)):
    try:
        user=get_current_user(request, None, db)
        return SessionInfo(logged_in=True,user_id=user.id,email=user.email)
    except HTTPException:
        return SessionInfo(logged_in=False)
