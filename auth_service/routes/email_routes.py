from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth_service.database.database import get_db
from auth_service.app.email_logic import email_instance

email_router = APIRouter()

@email_router.get("/confirm-email")
async def confirm_email(token: str, email: str, db: AsyncSession = Depends(get_db)):
    return await email_instance.confirm_email(email, token, db)
