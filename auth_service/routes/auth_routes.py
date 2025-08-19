from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth_service.database.schemas import UserResponse, UserCreate, UserLogin, TokenResponse
from auth_service.database.database import get_db
from auth_service.database.models import Token
from auth_service.app.jwt_handler import create_access_token, create_refresh_token
from auth_service.app.auth import register_instance, login_instance, logout_instance
from auth_service.core.security import oauth2_scheme
from datetime import datetime, timedelta
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter()

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await register_instance.register_user(user, db)
    return user

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(user: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    user = await login_instance.login_user(user.email, user.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    data={"id": user.id, "email": user.email, "username": user.username,
                                             "email_is_verified": user.email_is_verified}

    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    device_info = request.headers.get("User-Agent")

    existing_token = await db.execute(
        select(Token).filter(Token.user_id == user.id, Token.device_info == device_info)
    )
    existing_token = existing_token.scalar()

    if existing_token:
        existing_token.refresh_token = refresh_token
        existing_token.expires_at = datetime.utcnow() + timedelta(days=7)
    else:
        token = Token(
            user_id=user.id,
            device_info=device_info,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(token)

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60,
        refresh_token=refresh_token
    )

@auth_router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return await logout_instance.logout(request, db)

@auth_router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await login_instance.login_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"id": user.id, "email": user.email, "username": user.username})
    refresh_token = create_refresh_token(data={"id": user.id, "email": user.email, "username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "refresh_token": refresh_token
    }