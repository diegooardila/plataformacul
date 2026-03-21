from fastapi import APIRouter, HTTPException
from controllers.academic_periods_controller import *
from models.academic_periods_model import AcademicPeriod

router = APIRouter()

new_academic_period_controller = AcademicPeriodController()

@router.post("/create_academic_period", tags=["Academic Period"])
async def create_academic_period(academic_period: AcademicPeriod):
    rpta = new_academic_period_controller.create_academic_period(academic_period)
    return rpta

@router.get("/get_academic_period/{id_period}",response_model=AcademicPeriod, tags=["Academic Period"])
async def get_academic_period(id_period: int):
    rpta = new_academic_period_controller.get_academic_period(id_period)
    return rpta

@router.get("/get_academic_periods", tags=["Academic Period"])
async def get_academic_periods():
    rpta = new_academic_period_controller.get_academic_periods()
    return rpta

@router.put("/update_academic_period/{id_period}", tags=["Academic Period"])
async def update_academic_period(id_period: int, academic_period: AcademicPeriod):
    rpta = new_academic_period_controller.update_academic_period(id_period, academic_period)
    return rpta

@router.delete("/delete_academic_period/{id_period}", tags=["Academic Period"])
async def delete_academic_period(id_period: int):
    rpta = new_academic_period_controller.delete_academic_period(id_period)
    return rpta