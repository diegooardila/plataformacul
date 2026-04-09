from fastapi import APIRouter
from controllers.auth_controller import login_user, LoginRequest

router = APIRouter()

@router.post("/auth/login")
def login(request: LoginRequest):
    return login_user(request)
