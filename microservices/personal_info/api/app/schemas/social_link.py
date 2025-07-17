from pydantic import BaseModel, HttpUrl, field_serializer

class SocialLinkCreate(BaseModel):
    platform: str
    url: HttpUrl

    @field_serializer('url')
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

class SocialLinkUpdate(SocialLinkCreate):
    pass

class SocialLinkUpdatePartially(BaseModel):
    platform: str | None
    url: HttpUrl | None


class SocialLinkOut(SocialLinkCreate):
    model_config = {"from_attributes":True}
    id: int

