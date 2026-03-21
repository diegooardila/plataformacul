from pydantic import BaseModel

class Faculty(BaseModel):
    faculty_id: int | None = None
    faculty_name: str