from pydantic import BaseModel


class FeedItem(BaseModel):
    type: str
    branch: str
    link: str
    title: str
