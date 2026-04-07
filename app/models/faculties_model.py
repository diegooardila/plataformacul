from pydantic import BaseModel

class Faculty(BaseModel):
    faculty_id: int | None = None
    faculty_name: str
    created_at: str | None = None
    updated_at: str | None = None