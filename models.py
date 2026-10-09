from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class FamilyMember(Base):
    __tablename__ = "family_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    marital_status = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, default="Utah")
    zip_code = Column(String, nullable=False)
    license_years = Column(Integer, default=1)
    accidents = Column(Integer, default=0)
    violations = Column(Integer, default=0)
    coverage_type = Column(String, default="full")
    deductible = Column(Integer, default=500)
    liability_limit = Column(String, default="100/300/100")
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete")
    quotes = relationship("Quote", back_populates="member", cascade="all, delete")
    policies = relationship("Policy", back_populates="member", cascade="all, delete")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    year = Column(Integer, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    ownership = Column(String, default="owned")
    annual_mileage = Column(Integer, default=12000)
    primary_use = Column(String, default="commute")
    owner = relationship("FamilyMember", back_populates="vehicles")
    policies = relationship("Policy", back_populates="vehicle")

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    result = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    member = relationship("FamilyMember", back_populates="quotes")


class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    policy_type = Column(String, nullable=False, default="auto")
    carrier = Column(String, nullable=False)
    policy_number = Column(String, default="")
    status = Column(String, default="active")
    effective_date = Column(String, default="")
    expiration_date = Column(String, default="")
    billing_cycle = Column(String, default="monthly")
    premium_amount = Column(Integer, default=0)
    deductible = Column(Integer, default=500)
    liability_limit = Column(String, default="")
    agent_name = Column(String, default="")
    agent_phone = Column(String, default="")
    agent_email = Column(String, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    member = relationship("FamilyMember", back_populates="policies")
    vehicle = relationship("Vehicle", back_populates="policies")
    coverages = relationship("PolicyCoverage", back_populates="policy", cascade="all, delete")


class PolicyCoverage(Base):
    __tablename__ = "policy_coverages"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    name = Column(String, nullable=False)
    limit_amount = Column(String, default="")
    deductible = Column(Integer, default=0)
    notes = Column(String, default="")
    policy = relationship("Policy", back_populates="coverages")
