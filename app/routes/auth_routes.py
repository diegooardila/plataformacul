from fastapi import APIRouter, Request, Response

from controllers.auth_controller import login_user, logout_user, refresh_tokens, register_user
from models.auth_model import LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/auth/register", tags=["Auth"])
def register(data: RegisterRequest, response: Response):
    return register_user(data, response)


@router.post("/auth/login", tags=["Auth"])
def login(data: LoginRequest, response: Response):
    return login_user(data, response)


@router.post("/auth/refresh", tags=["Auth"])
def refresh(request: Request, response: Response):
    return refresh_tokens(request, response)


@router.post("/auth/logout", tags=["Auth"])
def logout(request: Request, response: Response):
    return logout_user(request, response)
