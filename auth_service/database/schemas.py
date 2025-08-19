from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    email_is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class ChangePasswordRequest(BaseModel):
    user_id: int
    new_password: str

class ChangeEmailRequest(BaseModel):
    user_id: int
    new_email: str

class ChangeUsernameRequest(BaseModel):
    user_id: int
    new_username: str

class DeleteUserRequest(BaseModel):
    user_id: int

