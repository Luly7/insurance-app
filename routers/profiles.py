from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/profiles", tags=["profiles"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def list_profiles(request: Request, db: Session = Depends(get_db)):
    members = db.query(models.FamilyMember).all()
    return templates.TemplateResponse(request=request, name="profiles.html", context={"members": members})

@router.get("/add", response_class=HTMLResponse)
def add_profile_form(request: Request):
    return templates.TemplateResponse(request=request, name="profile_form.html", context={"member": None, "action": "/profiles/add"})

@router.post("/add")
def add_profile(
    name: str = Form(...), age: int = Form(...), gender: str = Form(...),
    marital_status: str = Form(...), city: str = Form(...), zip_code: str = Form(...),
    license_years: int = Form(...), accidents: int = Form(0), violations: int = Form(0),
    coverage_type: str = Form("full"), deductible: int = Form(500),
    liability_limit: str = Form("100/300/100"), db: Session = Depends(get_db),
):
    member = models.FamilyMember(
        name=name, age=age, gender=gender, marital_status=marital_status,
        city=city, zip_code=zip_code, license_years=license_years,
        accidents=accidents, violations=violations, coverage_type=coverage_type,
        deductible=deductible, liability_limit=liability_limit,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return RedirectResponse(url=f"/profiles/{member.id}", status_code=303)

@router.get("/{member_id}", response_class=HTMLResponse)
def view_profile(member_id: int, request: Request, db: Session = Depends(get_db)):
    member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    quotes = db.query(models.Quote).filter(models.Quote.member_id == member_id).order_by(models.Quote.created_at.desc()).all()
    return templates.TemplateResponse(request=request, name="profile_detail.html", context={"member": member, "quotes": quotes})

@router.get("/{member_id}/edit", response_class=HTMLResponse)
def edit_profile_form(member_id: int, request: Request, db: Session = Depends(get_db)):
    member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    return templates.TemplateResponse(request=request, name="profile_form.html", context={"member": member, "action": f"/profiles/{member_id}/edit"})

@router.post("/{member_id}/edit")
def edit_profile(
    member_id: int, name: str = Form(...), age: int = Form(...),
    gender: str = Form(...), marital_status: str = Form(...),
    city: str = Form(...), zip_code: str = Form(...),
    license_years: int = Form(...), accidents: int = Form(0),
    violations: int = Form(0), coverage_type: str = Form("full"),
    deductible: int = Form(500), liability_limit: str = Form("100/300/100"),
    db: Session = Depends(get_db),
):
    member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    member.name = name; member.age = age; member.gender = gender
    member.marital_status = marital_status; member.city = city
    member.zip_code = zip_code; member.license_years = license_years
    member.accidents = accidents; member.violations = violations
    member.coverage_type = coverage_type; member.deductible = deductible
    member.liability_limit = liability_limit
    db.commit()
    return RedirectResponse(url=f"/profiles/{member_id}", status_code=303)

@router.post("/{member_id}/delete")
def delete_profile(member_id: int, db: Session = Depends(get_db)):
    member = db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()
    db.delete(member)
    db.commit()
    return RedirectResponse(url="/", status_code=303)
