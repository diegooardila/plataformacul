from pydantic import BaseModel

class Role(BaseModel):
    role_id: int | None = None
    role_name: str
    created_at: str | None = None
    updated_at: str | None = None