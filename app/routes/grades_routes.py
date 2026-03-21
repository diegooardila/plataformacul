from fastapi import APIRouter, HTTPException
from controllers.grades_controller import *
from models.grades_model import Grade

router = APIRouter()

new_grade = GradeController()

@router.post("/create_grade/", tags=["Grade"])
async def create_grade(grade: Grade):
    rpta = new_grade.create_grade(grade)
    return rpta

@router.get("/get_grade/{id_grade}",response_model=Grade, tags=["Grade"])
async def get_grade(id_grade: int):
    rpta = new_grade.get_grade(id_grade)
    return rpta

@router.get("/get_grades", tags=["Grade"])
async def get_grades():
    rpta = new_grade.get_grades()
    return rpta

@router.put("/update_grade/{id_grade}", tags=["Grade"])
async def update_grade(id_grade: int, grade: Grade):
    rpta = new_grade.update_grade(id_grade, grade)
    return rpta

@router.delete("/delete_grade/{id_grade}", tags=["Grade"])
async def delete_grade(id_grade: int):
    rpta = new_grade.delete_grade(id_grade)
    return rpta