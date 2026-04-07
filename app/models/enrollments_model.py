from pydantic import BaseModel
from datetime import datetime

class Enrollment(BaseModel):
    enrollment_id: int | None = None
    student_user_id: int
    course_id: int
    registration_date: datetime
    status_id: int
    created_at: str | None = None
    updated_at: str | None = None