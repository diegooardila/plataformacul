from pydantic import BaseModel
from datetime import date

class AcademicPeriod(BaseModel):
    period_id: int | None = None
    period_code: str
    start_date: date
    end_date: date
    created_at: str | None = None
    updated_at: str | None = None