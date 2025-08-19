import logging
from auth_service.database.models import Token
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from auth_service.app.jwt_handler import SECRET_KEY, ALGORITHM
from auth_service.core.security import oauth2_scheme
from auth_service.core.utils import generate_password, get_password_hash
from auth_service.database.models import User
from auth_service.database.database import get_db
from auth_service.mail.email_sender import send_resset_password_email


class UserData:
    def __init__(self):
        pass
#sosal
    @staticmethod
    async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    async def get_all_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users

    @staticmethod
    async def get_current_user_id(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("id")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        return user_id

    @staticmethod
    async def get_all_users_were_is_active(db: AsyncSession = Depends(get_db)):
        users = await db.execute(
            select(User).where(User.is_active == True)
        )
        return users.scalars().all()

class ChangeUserData(UserData):
    async def change_password(self, user_id: int, new_password: str, db: AsyncSession = Depends(get_db)):
        user = await self.get_user(user_id, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        new_hashed_password = get_password_hash(new_password)
        user.hashed_password = new_hashed_password
        db.add(user)
        await db.commit()
        logging.info("Password updated successfully")
        return {"message": "Password updated successfully"}

    async def change_email(self, user_id: int, new_email: EmailStr, db: AsyncSession = Depends(get_db)):
        user = await self.get_user(user_id, db)
        user.email = new_email
        db.add(user)
        await db.commit()
        return {"message": "Email updated successfully"}

    async def change_username(self, user_id: int, new_username: str, db: AsyncSession = Depends(get_db)):
        user = await self.get_user(user_id, db)
        user.username = new_username
        db.add(user)
        await db.commit()
        return {"message": "Username updated successfully"}

    async def delete_user(self, user_id: int, db: AsyncSession = Depends(get_db)):
        user = await self.get_user(user_id, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await db.execute(
            delete(Token).where(Token.user_id == user_id)
        )
        await db.delete(user)
        await db.commit()
        return {"message": "User deleted successfully"}


    async def reset_password(self, user_id: int, db: AsyncSession = Depends(get_db)):
        user = await self.get_user(user_id, db)
        new_password = generate_password()
        new_hashed_password = get_password_hash(new_password)
        user.hashed_password = new_hashed_password
        db.add(user)
        await db.commit()
        await send_resset_password_email(user.email, new_password)
        return {"message": "Password reset successfully, check your email for the new password"}


user_instance = UserData()
change_user_instance = ChangeUserData()