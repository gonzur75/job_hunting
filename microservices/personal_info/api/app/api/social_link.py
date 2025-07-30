
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.models.social_link import SocialLink
from app.schemas.social_link import SocialLinkOut, SocialLinkCreate, SocialLinkUpdatePartially

router = APIRouter(prefix="/social-links", tags=["Social Link"])

@router.post(
    "/",
    response_model=list[SocialLinkOut],
    status_code=status.HTTP_201_CREATED,
    summary = "Bulk add social links for current user",
    description = "Add multiple social links for current user",
)
async def add_social_links(
        links: Annotated[list[SocialLinkCreate], ...],
        db: AsyncSession = Depends(get_db)

) -> list[SocialLinkOut]:
    created_links: list[SocialLink] = []

    user_id = 1

    try:

        for link in links:
            item = SocialLink(user_id=user_id, **link.model_dump())
            db.add(item)
            created_links.append(item)
        await db.commit()

        for item in created_links:
            await db.refresh(item)

        return [SocialLinkOut.model_validate(item) for item in created_links]

    except SQLAlchemyError as err:

        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add social links: {err.__class__.__name__}")


@router.get("/", response_model=list[SocialLinkOut])
async def get_social_links(
        db: AsyncSessionLocal = Depends(get_db)
):
    stmt = select(SocialLink).where(SocialLink.user_id == 1)
    results = await db.execute(stmt)
    links = results.scalars().all()
    return links

@router.get("/{id}/", response_model=SocialLinkOut)
async def get_social_link(
        id: int,
        db: AsyncSessionLocal = Depends(get_db),
) -> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.id == id)
    results = await db.execute(stmt)
    link = results.scalars().first()
    return link

@router.patch("/{id}/", response_model=SocialLinkOut)
async def update_social_link(
        id: int,
        update_data: SocialLinkUpdatePartially,
        db: AsyncSessionLocal = Depends(get_db),
)-> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    results = await db.execute(stmt)
    link = results.scalars_one_or_more(stmt)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    for field, value in update_data.model_dump_update(exclude_unset=True).items():
        setattr(link, field, value)

    await db.commit()
    await db.refresh(link)
    return link

@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
        id: int,
        db: AsyncSessionLocal = Depends(get_db),
)-> None:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    result = await db.execute(stmt)
    link = result.scalars_one_or_none()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
