from pydantic import BaseModel


class CreateScheduleDTO(BaseModel):
    schedule_id: str
    schedule_type: str
    week: int
