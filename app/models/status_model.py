from pydantic import BaseModel

class Status(BaseModel):
    status_id: int | None = None
    status_name: str
    created_at: str | None = None
    updated_at: str | None = None