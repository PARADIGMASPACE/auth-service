from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.app.email_logic import email_instance
from auth_service.core.redis_client import redisClient
from auth_service.core.utils import generate_password, get_password_hash
from auth_service.database.schemas import ChangePasswordRequest, ChangeEmailRequest, ChangeUsernameRequest, \
    DeleteUserRequest
from auth_service.app.user_data import change_user_instance, user_instance
from auth_service.database.database import get_db
from auth_service.core.security import oauth2_scheme
from auth_service.mail.email_sender import send_resset_password_email, generate_reset_link

change_router = APIRouter()


@change_router.patch("/change-password")
async def change_password(data: ChangePasswordRequest, db: AsyncSession = Depends(get_db),
                          token: str = Depends(oauth2_scheme)):
    user_id = await user_instance.get_current_user_id(token)
    return await change_user_instance.change_password(user_id, data.new_password, db)


@change_router.patch("/change-email")
async def change_email(data: ChangeEmailRequest, db: AsyncSession = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    user_id = await user_instance.get_current_user_id(token)
    return await change_user_instance.change_email(user_id, data.new_email, db)


@change_router.patch("/change-username")
async def change_username(data: ChangeUsernameRequest, db: AsyncSession = Depends(get_db),
                          token: str = Depends(oauth2_scheme)):
    user_id = await user_instance.get_current_user_id(token)
    return await change_user_instance.change_username(user_id, data.new_username, db)
@change_router.delete("/delete-user")
async def delete_user(data: DeleteUserRequest, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = await user_instance.get_current_user_id(token)
    return await change_user_instance.delete_user(user_id, db)


@change_router.get("/reset-password")
async def reset_password(email: str, token_check_redis: str, db: AsyncSession = Depends(get_db)):
    if not await redisClient.key_exists(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    token_from_redis = await redisClient.get_token(email)
    if token_from_redis.decode("utf-8") != token_check_redis:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await email_instance.find_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_password = generate_password()
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await redisClient.delete_token(email)

    return {"message": "Password has been reset", "new_password": new_password}


@change_router.post("/request-password-reset")
async def request_password_reset(email: str, db: AsyncSession = Depends(get_db)):
    user = await email_instance.find_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_link = await generate_reset_link(email)
    await send_resset_password_email(email, reset_link)
    return {"message": "Password reset link has been sent to your email"}


