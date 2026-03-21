from fastapi import APIRouter, HTTPException
from controllers.users_controller import *
from models.users_model import User

router = APIRouter()

new_usuario = UserController()

@router.post("/create_usuario/", tags=["User"])
async def create_usuario(usuario: User):
    rpta = new_usuario.create_user(usuario)
    return rpta

@router.get("/get_usuario/{id_usuario}",response_model=User, tags=["User"])
async def get_usuario(id_usuario: int):
    rpta = new_usuario.get_user(id_usuario)
    return rpta

@router.get("/get_usuarios", tags=["User"])
async def get_usuarios():
    rpta = new_usuario.get_users()
    return rpta

@router.put("/update_usuario/{id_usuario}", tags=["User"])
async def update_usuario(id_usuario: int, usuario: User):
    rpta = new_usuario.update_user(id_usuario, usuario)
    return rpta

@router.delete("/delete_usuario/{id_usuario}", tags=["User"])
async def delete_usuario(id_usuario: int):
    rpta = new_usuario.delete_user(id_usuario)
    return rpta