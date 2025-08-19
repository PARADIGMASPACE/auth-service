import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from fastapi import HTTPException, Depends, status, Request
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from auth_service.core.utils import get_password_hash
from auth_service.database.schemas import UserCreate
from auth_service.database.models import User, Token
from auth_service.database.database import get_db
from auth_service.mail.email_sender import send_confirmation_email
from auth_service.database.models import Token
from auth_service.app.jwt_handler import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt


class Register:

    def __init__(self):
        pass

    @staticmethod
    async def is_user_exists(db: AsyncSession, user: UserCreate) -> User:
        result = await db.execute(select(User).where(or_(User.email == user.email, User.username == user.username)))
        return result.scalar()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def register_user(self, user: UserCreate, db: AsyncSession = Depends(get_db)):
        existing_user = await self.is_user_exists(db, user)

        if existing_user:
            if existing_user.email == user.email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
            if existing_user.username == user.username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already registered')
        new_user = await self.create_user(db, user)
        await send_confirmation_email(new_user.email)
        return new_user


class Login:
    @staticmethod
    async def login_user(email: str, password: str, db: AsyncSession = Depends(get_db)):
        from auth_service.app.email_logic import email_instance
        user = await email_instance.find_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        if not user.check_password(password):
            raise HTTPException(status_code=400, detail='Incorrect password')

        return user

    @staticmethod
    async def verify_refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("id")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token = await db.execute(select(Token).filter(Token.refresh_token == refresh_token))
        token = token.scalar()
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

class Logout:
    @staticmethod
    async def logout(request: Request, db: AsyncSession = Depends(get_db)):
        device_info = request.headers.get("User-Agent")
        token = await db.execute(
            select(Token).filter(Token.device_info == device_info)
        )
        token = token.scalar()
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
        await db.delete(token)
        await db.commit()
        return {"message": "Logged out successfully"}

logout_instance = Logout()
register_instance = Register()
login_instance = Login()
