from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    identity_document: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None
    email: str
    password: str
    role_id: int = 3
    faculty_id: Optional[int] = None
    status_id: int = 1


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int
    identity_document: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    second_last_name: Optional[str]
    email: str
    role_id: int
    faculty_id: Optional[int]
    status_id: int
