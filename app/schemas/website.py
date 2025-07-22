from pydantic import BaseModel, Field

class WebsiteRequest(BaseModel):
    url: str = Field(min_length=1)

class WebsiteCreate(WebsiteRequest):
    title: str
    markdown: list[str]
    owner_id: int