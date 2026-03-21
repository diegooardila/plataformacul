from pydantic import BaseModel

class Status(BaseModel):
    status_id: int | None = None
    status_name: str