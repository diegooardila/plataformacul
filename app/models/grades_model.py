from decimal import Decimal
from pydantic import BaseModel

class Grade(BaseModel):
    grade_id: int | None = None
    enrollment_id: int
    final_grade: Decimal
    observations: str | None = None