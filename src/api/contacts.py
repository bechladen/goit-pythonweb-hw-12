from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repository.contacts import ContactsRepository
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    try:
        return await repo.create(body, user)
    except IntegrityError:
        # Найчастіша причина тут — порушення унікальності email.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Контакт з такою електронною адресою вже існує",
        )


@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    q: str | None = Query(default=None, description="Пошук по імені/прізвищу/email (одним рядком)"),
    first_name: str | None = Query(default=None, description="Пошук за іменем"),
    last_name: str | None = Query(default=None, description="Пошук за прізвищем"),
    email: str | None = Query(default=None, description="Пошук за email"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return await repo.list(
        skip=skip,
        limit=limit,
        user=user,
        q=q,
        q_first_name=first_name,
        q_last_name=last_name,
        q_email=email,
    )


@router.get("/birthdays", response_model=list[ContactResponse])
async def upcoming_birthdays(
    days: int = Query(default=7, ge=1, le=365, description="Горизонт пошуку у днях"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return await repo.upcoming_birthdays(days=days, user=user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = await repo.get_by_id(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не знайдено",
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = await repo.update(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не знайдено",
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = await repo.delete(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не знайдено",
        )
    return contact

