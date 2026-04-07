from pydantic import BaseModel

class User(BaseModel):
    user_id: int | None = None
    identity_document: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    second_last_name: str | None = None
    email: str
    password_hash: str
    role_id: int
    faculty_id: int | None = None
    status_id: int
    created_at: str | None = None
    updated_at: str | None = None