from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/policies", tags=["policies"])
templates = Jinja2Templates(directory="templates")

POLICY_TYPES = ["auto", "home", "renters", "umbrella", "life", "health", "dental", "vision", "other"]
STATUSES = ["active", "quoting", "expired", "cancelled"]


@router.get("/", response_class=HTMLResponse)
def list_policies(request: Request, db: Session = Depends(get_db)):
    policies = db.query(models.Policy).order_by(models.Policy.policy_type, models.Policy.carrier).all()
    members = db.query(models.FamilyMember).all()
    return templates.TemplateResponse(
        request=request,
        name="policies.html",
        context={"policies": policies, "members": members},
    )


@router.get("/add", response_class=HTMLResponse)
def add_policy_form(request: Request, db: Session = Depends(get_db), member_id: int | None = None):
    members = db.query(models.FamilyMember).all()
    vehicles = db.query(models.Vehicle).all()
    return templates.TemplateResponse(
        request=request,
        name="policy_form.html",
        context={
            "policy": None,
            "members": members,
            "vehicles": vehicles,
            "policy_types": POLICY_TYPES,
            "statuses": STATUSES,
            "selected_member_id": member_id,
            "action": "/policies/add",
        },
    )


@router.post("/add")
def add_policy(
    member_id: int = Form(...),
    vehicle_id: str = Form(""),
    policy_type: str = Form("auto"),
    carrier: str = Form(...),
    policy_number: str = Form(""),
    status: str = Form("active"),
    effective_date: str = Form(""),
    expiration_date: str = Form(""),
    billing_cycle: str = Form("monthly"),
    premium_amount: int = Form(0),
    deductible: int = Form(500),
    liability_limit: str = Form(""),
    agent_name: str = Form(""),
    agent_phone: str = Form(""),
    agent_email: str = Form(""),
    notes: str = Form(""),
    coverage_names: list[str] = Form([]),
    coverage_limits: list[str] = Form([]),
    coverage_deductibles: list[str] = Form([]),
    db: Session = Depends(get_db),
):
    policy = models.Policy(
        member_id=member_id,
        vehicle_id=int(vehicle_id) if vehicle_id else None,
        policy_type=policy_type,
        carrier=carrier,
        policy_number=policy_number,
        status=status,
        effective_date=effective_date,
        expiration_date=expiration_date,
        billing_cycle=billing_cycle,
        premium_amount=premium_amount,
        deductible=deductible,
        liability_limit=liability_limit,
        agent_name=agent_name,
        agent_phone=agent_phone,
        agent_email=agent_email,
        notes=notes,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    _save_coverages(db, policy.id, coverage_names, coverage_limits, coverage_deductibles)
    return RedirectResponse(url=f"/policies/{policy.id}", status_code=303)


@router.get("/{policy_id}", response_class=HTMLResponse)
def view_policy(policy_id: int, request: Request, db: Session = Depends(get_db)):
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    return templates.TemplateResponse(request=request, name="policy_detail.html", context={"policy": policy})


@router.get("/{policy_id}/edit", response_class=HTMLResponse)
def edit_policy_form(policy_id: int, request: Request, db: Session = Depends(get_db)):
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    members = db.query(models.FamilyMember).all()
    vehicles = db.query(models.Vehicle).all()
    return templates.TemplateResponse(
        request=request,
        name="policy_form.html",
        context={
            "policy": policy,
            "members": members,
            "vehicles": vehicles,
            "policy_types": POLICY_TYPES,
            "statuses": STATUSES,
            "selected_member_id": policy.member_id if policy else None,
            "action": f"/policies/{policy_id}/edit",
        },
    )


@router.post("/{policy_id}/edit")
def edit_policy(
    policy_id: int,
    member_id: int = Form(...),
    vehicle_id: str = Form(""),
    policy_type: str = Form("auto"),
    carrier: str = Form(...),
    policy_number: str = Form(""),
    status: str = Form("active"),
    effective_date: str = Form(""),
    expiration_date: str = Form(""),
    billing_cycle: str = Form("monthly"),
    premium_amount: int = Form(0),
    deductible: int = Form(500),
    liability_limit: str = Form(""),
    agent_name: str = Form(""),
    agent_phone: str = Form(""),
    agent_email: str = Form(""),
    notes: str = Form(""),
    coverage_names: list[str] = Form([]),
    coverage_limits: list[str] = Form([]),
    coverage_deductibles: list[str] = Form([]),
    db: Session = Depends(get_db),
):
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    policy.member_id = member_id
    policy.vehicle_id = int(vehicle_id) if vehicle_id else None
    policy.policy_type = policy_type
    policy.carrier = carrier
    policy.policy_number = policy_number
    policy.status = status
    policy.effective_date = effective_date
    policy.expiration_date = expiration_date
    policy.billing_cycle = billing_cycle
    policy.premium_amount = premium_amount
    policy.deductible = deductible
    policy.liability_limit = liability_limit
    policy.agent_name = agent_name
    policy.agent_phone = agent_phone
    policy.agent_email = agent_email
    policy.notes = notes
    db.query(models.PolicyCoverage).filter(models.PolicyCoverage.policy_id == policy_id).delete()
    db.commit()
    _save_coverages(db, policy_id, coverage_names, coverage_limits, coverage_deductibles)
    return RedirectResponse(url=f"/policies/{policy_id}", status_code=303)


@router.post("/{policy_id}/delete")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    db.delete(policy)
    db.commit()
    return RedirectResponse(url="/policies", status_code=303)


def _save_coverages(db, policy_id, names, limits, deductibles):
    for i, name in enumerate(names):
        name = (name or "").strip()
        if not name:
            continue
        limit = limits[i] if i < len(limits) else ""
        raw_ded = deductibles[i] if i < len(deductibles) else "0"
        try:
            ded = int(raw_ded or 0)
        except ValueError:
            ded = 0
        db.add(models.PolicyCoverage(
            policy_id=policy_id,
            name=name,
            limit_amount=limit,
            deductible=ded,
        ))
    db.commit()
