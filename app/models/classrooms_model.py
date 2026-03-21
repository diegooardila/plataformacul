from pydantic import BaseModel

class Classroom(BaseModel):
    classroom_id: int | None = None
    classroom_code: str
    max_capacity: int
    status: int