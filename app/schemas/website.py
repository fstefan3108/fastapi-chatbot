from pydantic import BaseModel, HttpUrl

class WebsiteRequest(BaseModel):
    url: HttpUrl

class WebsiteResponse(BaseModel):
    id: int
    url: HttpUrl
    title: str
    api_key: str

    class Config:
        from_attributes = True

class WebsiteCreate(WebsiteRequest):
    title: str
    owner_id: int