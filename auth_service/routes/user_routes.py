from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from auth_service.app.jwt_handler import decode_token
from auth_service.core.security import oauth2_scheme
from auth_service.database.database import get_db
from auth_service.database.schemas import UserResponse
from auth_service.app.user_data import user_instance

users_router = APIRouter()


@users_router.get("/get-all-users", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return await user_instance.get_all_users(db)

@users_router.get("/get-user-by-id", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return await user_instance.get_user_by_id(user_id, db)

@users_router.get("/get-current-user", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = await user_instance.get_current_user_id(token)
    return await user_instance.get_user(user_id, db)

@users_router.get("/get-all-users-were-is-active", response_model=List[UserResponse])
async def get_all_users_were_is_active(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return await user_instance.get_all_users_were_is_active(db)