from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repository.users import UsersRepository
from src.schemas import LoginRequest, RequestEmail, TokenResponse, UserCreate, UserResponse
from src.services.auth import create_access_token, get_email_from_token
from src.services.email import send_verification_email
from src.services.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    repo = UsersRepository(db)

    if await repo.exists_by_email_or_username(email=body.email, username=body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists",
        )

    user = await repo.create(body, hashed_password=hash_password(body.password))
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username,
        base_url=str(request.base_url),
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UsersRepository(db)
    user = await repo.get_by_username(body.username)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = get_email_from_token(token)
    repo = UsersRepository(db)
    user = await repo.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await repo.confirm_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    repo = UsersRepository(db)
    user = await repo.get_by_email(str(body.email))

    if user and user.confirmed:
        return {"message": "Email already confirmed"}

    # Return same response regardless of existence to avoid email enumeration
    if user:
        background_tasks.add_task(
            send_verification_email,
            email=user.email,
            username=user.username,
            base_url=str(request.base_url),
        )
    return {"message": "Check your email for verification link"}

