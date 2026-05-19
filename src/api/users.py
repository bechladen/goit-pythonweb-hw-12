from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.schemas import UserResponse
from src.services.auth import get_current_user
from src.repository.users import UsersRepository
from src.database import get_db
from src.services.cloudinary_upload import upload_avatar

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def me(request: Request, user=Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    avatar_url = upload_avatar(file_obj=file.file, username=user.username)
    if avatar_url is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured",
        )

    repo = UsersRepository(db)
    return await repo.update_avatar(user=user, avatar_url=avatar_url)

