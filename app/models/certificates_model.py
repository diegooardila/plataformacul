from datetime import datetime
from pydantic import BaseModel

class Certificate(BaseModel):
    certificate_id: int | None = None
    enrollment_id: int
    verification_code: str
    issue_date: datetime
    created_at: str | None = None
    updated_at: str | None = None