from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/vehicles", tags=["vehicles"])
templates = Jinja2Templates(directory="templates")

@router.get("/{member_id}/add", response_class=HTMLResponse)
def add_vehicle_form(member_id: int, request: Request, db: Session = Depends(get_db)):
    member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    return templates.TemplateResponse(request=request, name="vehicle_form.html", context={"member": member, "vehicle": None})

@router.post("/{member_id}/add")
def add_vehicle(
    member_id: int, year: int = Form(...), make: str = Form(...),
    model: str = Form(...), ownership: str = Form("owned"),
    annual_mileage: int = Form(12000), primary_use: str = Form("commute"),
    db: Session = Depends(get_db),
):
    vehicle = models.Vehicle(
        member_id=member_id, year=year, make=make, model=model,
        ownership=ownership, annual_mileage=annual_mileage, primary_use=primary_use,
    )
    db.add(vehicle)
    db.commit()
    return RedirectResponse(url=f"/profiles/{member_id}", status_code=303)

@router.post("/{vehicle_id}/delete")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    member_id = vehicle.member_id
    db.delete(vehicle)
    db.commit()
    return RedirectResponse(url=f"/profiles/{member_id}", status_code=303)
