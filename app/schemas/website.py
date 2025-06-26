from pydantic import BaseModel, Field


class WebsiteRequest(BaseModel):
    url: str = Field(min_length=1)



