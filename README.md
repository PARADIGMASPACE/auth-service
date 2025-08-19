# Authentication Service (FastAPI)

A production‑ready authentication service built with FastAPI. It provides registration, login, logout, email
verification, password reset, and JWT token management with refresh tokens. The service is containerized and prepared
for deployment.

## Overview

- JWT authentication: short‑lived access tokens and long‑lived refresh tokens
- Per‑device sessions (refresh token stored with device info)
- Email verification flow (Redis token storage)
- Password reset via secure email link
- User profile updates (email, username, password), account deletion
- Async PostgreSQL via SQLAlchemy
- Redis for email/token workflows
- Alembic migrations

## Architecture

- FastAPI app exposes REST endpoints
- PostgreSQL stores users and refresh tokens
- Redis stores temporary email/password reset tokens
- SMTP delivers transactional emails (confirmation, password reset)

## Tech Stack

- FastAPI, Pydantic
- SQLAlchemy (async) + PostgreSQL
- Redis (redis-py asyncio)
- JWT (PyJWT)
- Passlib/bcrypt for password hashing
- FastAPI‑Mail for SMTP
- Docker, Docker Compose

## Project Structure

```auth_service
├── auth_service
│   ├── app
│   │   ├── auth.py
│   │   ├── email_logic.py
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   ├── main.py
│   │   └── user_data.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── redis_client.py
│   │   ├── security.py
│   │   └── utils.py
│   ├── database
│   │   ├── alembic.ini
│   │   ├── database.py
│   │   ├── Dockerfile
│   │   ├── __init__.py
│   │   ├── init.sql
│   │   ├── migrations
│   │   │   ├── env.py
│   │   │   ├── README
│   │   │   └── script.py.mako
│   │   ├── models.py
│   │   └── schemas.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── mail
│   │   ├── email_sender.py
│   │   ├── __init__.py
│   │   └── templates
│   │       ├── __init__.py
│   │       ├── password_reset.html
│   │       └── registration_confirmation.html
│   ├── requirements.txt
│   └── routes
│       ├── auth_routes.py
│       ├── change_routes.py
│       ├── email_routes.py
│       ├── __init__.py
│       ├── token_routes.py
│       └── user_routes.py
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Gmail (or other SMTP) account with app password

### Environment Variables

Create a .env file at the project root (213/):

```
SECRET_KEY=your-super-secret-jwt-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
```

Notes:

- Database connection for the app is configured in auth_service/database/database.py (defaults to postgresql+asyncpg:
  //root:root@auth-db:5432/auth_db expected by docker-compose).
- Redis defaults to host "redis", port 6379 (see core/redis_client.py). No env required by default.

### Run with Docker

```
docker-compose up --build 
```

Open API docs when the service is up:

- Swagger UI: http://localhost:8001/docs
- ReDoc:      http://localhost:8001/redoc

### Migrations

If migrations are required (first run or after model changes):

```
docker-compose exec auth-service alembic upgrade head
```

## API Overview

Base URL: http://localhost:8001

Authentication

- POST /auth/register — create user (email, username, password)
- POST /auth/login — get access_token and refresh_token
- POST /auth/logout — invalidate current device session (requires Authorization)
- POST /auth/token — OAuth2 password flow (alt login)

Email

- GET /email/confirm-email?token=...&email=... — confirm email

Profile & Account

- PATCH /change/change-password — update password (Authorization required)
- PATCH /change/change-email — update email (Authorization required)
- PATCH /change/change-username — update username (Authorization required)
- DELETE /change/delete-user — delete account (Authorization required)

Password Reset

- POST /change/request-password-reset?email=... — receive reset link by email
- GET /change/reset-password?token_check_redis=...&email=... — complete reset and return a new password

Users (examples; access rules depend on implementation)

- GET /users/get-current-user — current user profile
- GET /users/get-all-users — list users (admin)
- GET /users/get-user-by-id/{id}

## Security

- Passwords are hashed using bcrypt (Passlib)
- JWT HS256 with configurable secret; access tokens are short‑lived, refresh tokens longer‑lived
- Per‑device refresh tokens stored with device user‑agent, allowing independent logout per device
- Email verification is mandatory for full access (enforced at business logic level)
- CORS configured for integration with web frontends

## Configuration Notes

- JWT settings are in app/jwt_handler.py
- Database engine/session are in database/database.py
- Email SMTP settings are in mail/email_sender.py and read from .env
- Redis client is in core/redis_client.py (async redis-py)

## What to Review (for hiring managers)

- Data models: database/models.py (User, Token)
- Auth flows and token handling: app/auth.py, app/jwt_handler.py, routes/auth_routes.py
- Email flows and Redis integration: app/email_logic.py, mail/email_sender.py, core/redis_client.py
- API surface and request models: routes/, database/schemas.py
- Async DB access patterns and session management: database/database.py

## Deployment

- The service is packaged with Docker and docker-compose for local and production‑like environments.
- For production, provide proper SECRET_KEY, SMTP credentials, and run migrations.
- Configure external Postgres/Redis endpoints if not using the bundled Compose services.
