from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth_service.database.schemas import TokenRefresh, TokenRefreshResponse
from auth_service.database.database import get_db
from auth_service.app.jwt_handler import create_access_token, create_refresh_token
from auth_service.app.auth import login_instance

token_router = APIRouter()

@token_router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(token_refresh: TokenRefresh, db: AsyncSession = Depends(get_db)):
    user = await login_instance.verify_refresh_token(token_refresh.refresh_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    data={"id": user.id, "email": user.email, "username": user.username}

    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "expires_in": 30 * 60}