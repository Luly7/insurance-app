"""Load known household insurance facts into insurance.db without inventing policy numbers."""
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

member = db.query(models.FamilyMember).filter(models.FamilyMember.name == "Lourdes Castleton").first()
if not member:
    member = models.FamilyMember(
        name="Lourdes Castleton",
        age=54,
        gender="Female",
        marital_status="Married",
        city="Heber City",
        state="Utah",
        zip_code="84032",
        license_years=20,
        accidents=1,
        violations=0,
        coverage_type="full",
        deductible=500,
        liability_limit="100/300/100",
    )
    db.add(member)
    db.commit()
    db.refresh(member)

vehicle = db.query(models.Vehicle).filter(
    models.Vehicle.member_id == member.id,
    models.Vehicle.year == 2020,
    models.Vehicle.make == "Toyota",
    models.Vehicle.model == "RAV4",
).first()
if not vehicle:
    vehicle = models.Vehicle(
        member_id=member.id,
        year=2020,
        make="Toyota",
        model="RAV4",
        ownership="owned",
        annual_mileage=12000,
        primary_use="commute",
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

existing = db.query(models.Policy).filter(
    models.Policy.member_id == member.id,
    models.Policy.policy_type == "auto",
    models.Policy.vehicle_id == vehicle.id,
).first()

if not existing:
    policy = models.Policy(
        member_id=member.id,
        vehicle_id=vehicle.id,
        policy_type="auto",
        carrier="Not recorded yet",
        policy_number="",
        status="quoting",
        effective_date="",
        expiration_date="",
        billing_cycle="monthly",
        premium_amount=0,
        deductible=500,
        liability_limit="100/300/100",
        notes=(
            "Seeded from existing household data: Lourdes Castleton, Heber City UT 84032, "
            "2020 Toyota RAV4, full coverage, $500 deductible, 100/300/100 liability. "
            "Replace carrier, policy number, premium, and dates with the real declarations page."
        ),
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    for name, limit, ded in [
        ("Bodily injury liability", "100/300", 0),
        ("Property damage liability", "100", 0),
        ("Collision", "Actual cash value", 500),
        ("Comprehensive", "Actual cash value", 500),
        ("Uninsured motorist", "100/300", 0),
    ]:
        db.add(models.PolicyCoverage(
            policy_id=policy.id,
            name=name,
            limit_amount=limit,
            deductible=ded,
        ))
    db.commit()
    print(f"Added auto policy {policy.id} for {member.name}")
else:
    print(f"Auto policy already exists (id={existing.id})")

print("Policies in database:", db.query(models.Policy).count())
db.close()
