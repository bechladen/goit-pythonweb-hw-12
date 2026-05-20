from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хешує пароль (bcrypt)."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Перевіряє пароль проти хеша."""
    return pwd_context.verify(password, hashed_password)

