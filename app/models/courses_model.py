from pydantic import BaseModel

class Courses(BaseModel):
    course_id: int | None = None
    course_code: str
    course_name: str
    max_capacity: int
    schedule : str
    teacher_user_id: int
    clasroom: str
    period_id: int
    status: int
    created_at: str | None = None
    updated_at: str | None = None