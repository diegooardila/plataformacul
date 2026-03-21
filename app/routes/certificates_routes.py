from fastapi import APIRouter, HTTPException
from controllers.certificates_controller import *
from models.certificates_model import Certificate

router = APIRouter()

new_certificate = CertificateController()

@router.post("/create_certificate/", tags=["Certificate"])
async def create_certificate(certificate: Certificate):
    rpta = new_certificate.create_certificate(certificate)
    return rpta

@router.get("/get_certificate/{id_certificate}",response_model=Certificate, tags=["Certificate"])
async def get_certificate(id_certificate: int):
    rpta = new_certificate.get_certificate(id_certificate)
    return rpta

@router.get("/get_certificates", tags=["Certificate"])
async def get_certificates():
    rpta = new_certificate.get_certificates()
    return rpta

@router.put("/update_certificate/{id_certificate}", tags=["Certificate"])
async def update_certificate(id_certificate: int, certificate: Certificate):
    rpta = new_certificate.update_certificate(id_certificate, certificate)
    return rpta

@router.delete("/delete_certificate/{id_certificate}", tags=["Certificate"])
async def delete_certificate(id_certificate: int):
    rpta = new_certificate.delete_certificate(id_certificate)
    return rpta