from fastapi import APIRouter, HTTPException
from controllers.enrollments_controller import *
from models.enrollments_model import Enrollment

router = APIRouter()

new_enrollment = EnrollmentController()

@router.post("/create_enrollment/", tags=["Enrollment"])
async def create_enrollment(enrollment: Enrollment):
    rpta = new_enrollment.create_enrollment(enrollment)
    return rpta

@router.get("/get_enrollment/{enrollment_id}",response_model=Enrollment, tags=["Enrollment"])
async def get_enrollment(enrollment_id: int):
    rpta = new_enrollment.get_enrollment(enrollment_id)
    return rpta

@router.get("/get_enrollments", tags=["Enrollment"])
async def get_enrollments():
    rpta = new_enrollment.get_enrollments()
    return rpta

@router.put("/update_enrollment/{enrollment_id}", tags=["Enrollment"])
async def update_enrollment(enrollment_id: int, enrollment: Enrollment):
    rpta = new_enrollment.update_enrollment(enrollment_id, enrollment)
    return rpta

@router.delete("/delete_enrollment/{enrollment_id}", tags=["Enrollment"])
async def delete_enrollment(enrollment_id: int):
    rpta = new_enrollment.delete_enrollment(enrollment_id)
    return rpta
