from fastapi import APIRouter, HTTPException
from controllers.courses_controller import *
from models.courses_model import Courses

router = APIRouter()

new_course = CoursesController()

@router.post("/create_course/", tags=["Course"])
async def create_course(course: Courses):
    rpta = new_course.create_course(course)
    return rpta

@router.get("/get_course/{id_course}",response_model=Courses, tags=["Course"])
async def get_course(id_course: int):
    rpta = new_course.get_course(id_course)
    return rpta

@router.get("/get_courses", tags=["Course"])
async def get_courses():
    rpta = new_course.get_courses()
    return rpta

@router.put("/update_course/{id_course}", tags=["Course"])
async def update_course(id_course: int, course: Courses):
    rpta = new_course.update_course(id_course, course)
    return rpta

@router.delete("/delete_course/{id_course}", tags=["Course"])
async def delete_course(id_course: int):
    rpta = new_course.delete_course(id_course)
    return rpta
