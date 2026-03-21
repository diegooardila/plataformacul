from fastapi import APIRouter, HTTPException
from controllers.roles_controller import *
from models.roles_model import Role

router = APIRouter()

new_role = RoleController()

@router.post("/create_role/", tags=["Role"])
async def create_role(role: Role):
    rpta = new_role.create_role(role)
    return rpta

@router.get("/get_role/{id_role}",response_model=Role, tags=["Role"])
async def get_role(id_role: int):
    rpta = new_role.get_role(id_role)
    return rpta

@router.get("/get_roles", tags=["Role"])
async def get_roles():
    rpta = new_role.get_roles()
    return rpta

@router.put("/update_role/{id_role}", tags=["Role"])
async def update_role(id_role: int, role: Role):
    rpta = new_role.update_role(id_role, role)
    return rpta

@router.delete("/delete_role/{id_role}", tags=["Role"])
async def delete_role(id_role: int):
    rpta = new_role.delete_role(id_role)
    return rpta

@router.post("/create_course_from_admin/", tags=["Admin"])
async def create_course_from_admin(course: Courses):
    rpta = new_role.create_course_from_admin(course)
    return rpta

@router.put("/update_course_from_admin/{id_course}", tags=["Admin"])
async def update_course_from_admin(id_course: int, course: Courses):
    rpta = new_role.update_course_from_admin(id_course, course)
    return rpta

@router.delete("/delete_course_from_admin/{id_course}", tags=["Admin"])
async def delete_course_from_admin(id_course: int):
    rpta = new_role.delete_course_from_admin(id_course)
    return rpta