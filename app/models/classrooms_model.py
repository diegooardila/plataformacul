from pydantic import BaseModel

class Classroom(BaseModel):
    classroom_id: int | None = None
    classroom_code: str
    max_capacity: int
    status: int
    created_at: str | None = None
    updated_at: str | None = None