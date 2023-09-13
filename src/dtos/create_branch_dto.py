from pydantic import BaseModel


class CreateBranchDTO(BaseModel):
    branch_id: str
    branch_type: str
    branch_link: str
