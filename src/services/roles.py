from fastapi import Depends, HTTPException, status

from src.services.auth import get_current_user


async def require_admin(user=Depends(get_current_user)):
    """Залежність FastAPI: пропускає лише користувача з роллю `admin`."""
    if getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

