from passlib.context import CryptContext
import string
import random
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from uuid import uuid4


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_token_for_email() -> str:
    return str(uuid4())


def generate_password():
    length = random.randint(16,24)
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

