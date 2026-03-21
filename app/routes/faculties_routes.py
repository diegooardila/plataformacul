from fastapi import APIRouter, HTTPException
from controllers.faculties_controller import *
from models.faculties_model import Faculty

router = APIRouter()

new_faculty = FacultyController()

@router.post("/create_faculty", tags=["Faculty"])
async def create_faculty(faculty: Faculty):
    rpta = new_faculty.create_faculty(faculty)
    return rpta

@router.get("/get_faculty/{id_faculty}",response_model=Faculty, tags=["Faculty"])
async def get_faculty(id_faculty: int):
    rpta = new_faculty.get_faculty(id_faculty)
    return rpta

@router.get("/get_faculties", tags=["Faculty"])
async def get_faculties():
    rpta = new_faculty.get_faculties()
    return rpta

@router.put("/update_faculty/{id_faculty}", tags=["Faculty"])
async def update_faculty(id_faculty: int, faculty: Faculty):
    rpta = new_faculty.update_faculty(id_faculty, faculty)
    return rpta

@router.delete("/delete_faculty/{id_faculty}", tags=["Faculty"])
async def delete_faculty(id_faculty: int):
    rpta = new_faculty.delete_faculty(id_faculty)
    return rpta