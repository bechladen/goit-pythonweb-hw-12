from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repository.users import UsersRepository
from src.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(*, subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_email_token(*, email: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)
    payload = {
        "sub": email,
        "scope": "email_confirm",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_email_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("scope") != "email_confirm":
            raise ValueError("Invalid scope")
        email: str | None = payload.get("sub")
        if not email:
            raise ValueError("Missing sub")
        return email
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        ) from e


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = UsersRepository(db)
    user = await repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user

