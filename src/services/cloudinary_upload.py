import cloudinary
import cloudinary.uploader

from src.settings import settings


def _is_cloudinary_configured() -> bool:
    required = [settings.CLOUDINARY_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]
    return all(required)


def upload_avatar(*, file_obj, username: str) -> str | None:
    """
    Завантажує аватар у Cloudinary та повертає трансформований URL.

    Повертає `None`, якщо Cloudinary не налаштований.
    """
    if not _is_cloudinary_configured():
        return None

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    public_id = f"ContactsAPI/avatars/{username}"
    result = cloudinary.uploader.upload(file_obj, public_id=public_id, overwrite=True)
    version = result.get("version")

    return cloudinary.CloudinaryImage(public_id).build_url(
        width=250,
        height=250,
        crop="fill",
        version=version,
    )

