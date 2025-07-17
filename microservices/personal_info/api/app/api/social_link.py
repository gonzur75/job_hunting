from http.client import HTTPException

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, get_db
from app.models.social_link import SocialLink
from app.schemas.social_link import SocialLinkOut, SocialLinkCreate, SocialLinkUpdatePartially

router = APIRouter(prefix="/social-links", tags=["Social Link"])

@router.post("/", response_model=list[SocialLinkOut])
async def get_social_links(
        links: list[SocialLinkCreate],
        db: AsyncSessionLocal = Depends(get_db)

):
    created = []
    user_id = 1
    for link in links:
        item = SocialLink(user_id=user_id, **link.model_dump())
        db.add(item)
        created.append(item)

    await db.commit()

    for item in created:
        await db.refresh(item)

    return created

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
