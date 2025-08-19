import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from auth_service.routes.auth_routes import auth_router
from auth_service.routes.email_routes import email_router
from auth_service.routes.user_routes import users_router
from auth_service.routes.token_routes import token_router
from auth_service.routes.change_routes import change_router

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

app = FastAPI(middleware=middleware)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(email_router, prefix="/email", tags=["email"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(token_router, prefix="/auth/token", tags=["token"])
app.include_router(change_router, prefix="/change", tags=["change"])