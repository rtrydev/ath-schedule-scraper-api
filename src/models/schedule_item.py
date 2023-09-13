from pydantic import BaseModel


class ScheduleItem(BaseModel):
    id: str
    type: str
    title: str
