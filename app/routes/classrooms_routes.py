from fastapi import APIRouter, HTTPException
from controllers.classrooms_controller import *
from models.classrooms_model import Classroom

router = APIRouter()

new_classroom = ClassroomController()


@router.post("/create_classroom/", tags=["Classroom"])
async def create_classroom(classroom: Classroom):
    rpta = new_classroom.create_classroom(classroom)
    return rpta


@router.get("/get_classroom/{id_classroom}",response_model=Classroom, tags=["Classroom"])
async def get_classroom(id_classroom: int):
    rpta = new_classroom.get_classroom(id_classroom)
    return rpta

@router.get("/get_classrooms", tags=["Classroom"])
async def get_classrooms():
    rpta = new_classroom.get_classrooms()
    return rpta

@router.put("/update_classroom/{id_classroom}", tags=["Classroom"])
async def update_classroom(id_classroom: int, classroom: Classroom):
    rpta = new_classroom.update_classroom(id_classroom, classroom)
    return rpta

@router.delete("/delete_classroom/{id_classroom}", tags=["Classroom"])
async def delete_classroom(id_classroom: int):
    rpta = new_classroom.delete_classroom(id_classroom)
    return rpta

