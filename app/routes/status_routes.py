from fastapi import APIRouter, HTTPException
from controllers.status_controller import *
from models.status_model import Status

router = APIRouter()

new_status = StatusController()

@router.post("/create_status/", tags=["Status"])
async def create_status(status: Status):
    rpta = new_status.create_status(status)
    return rpta

@router.get("/get_status/{id_status}",response_model=Status, tags=["Status"])
async def get_status(id_status: int):
    rpta = new_status.get_status(id_status)
    return rpta

@router.get("/get_statuses", tags=["Status"])
async def get_statuses():
    rpta = new_status.get_statuses()
    return rpta

@router.put("/update_status/{id_status}", tags=["Status"])
async def update_status(id_status: int, status: Status):
    rpta = new_status.update_status(id_status, status)
    return rpta

@router.delete("/delete_status/{id_status}", tags=["Status"])
async def delete_status(id_status: int):
    rpta = new_status.delete_status(id_status)
    return rpta