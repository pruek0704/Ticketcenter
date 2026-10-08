"""Persisted administration controls. Every management route requires an active admin."""
from datetime import datetime, timedelta, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from .auth import current_user, hash_password
from .db import get_db
from .models import AdminAudit, ServiceCategory, SystemSettings, Ticket, User
from .departments import Department, DEPARTMENT_CODES, DEPARTMENT_NAMES, DEFAULT_CATALOG
from .realtime import publish

router = APIRouter(prefix="/api")
DEFAULT_SETTINGS = {"organization_name": "บริษัท ตัวอย่าง จำกัด", "announcement": "", "accepting_tickets": True, "aging_hours": 24}

def require_admin(user: User = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user

def audit(db, actor, action, target, details):
    db.add(AdminAudit(actor_id=actor.id, action=action, target=target, details=details))

def settings_data(db):
    row = db.get(SystemSettings, 1)
    return {k: getattr(row, k) for k in DEFAULT_SETTINGS} if row else DEFAULT_SETTINGS.copy()

def catalog_data(db):
    rows = {row.category: row for row in db.scalars(select(ServiceCategory)).all()}
    return [{**item, **({k: getattr(rows[item["category"]], k) for k in ("label", "description", "is_active")} if item["category"] in rows else {}), "department": item["category"]} for item in DEFAULT_CATALOG]

class SettingsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    organization_name: str = Field(min_length=2, max_length=100)
    announcement: str = Field(max_length=1000)
    accepting_tickets: bool
    aging_hours: int = Field(ge=1, le=720)

class AccountInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    display_name: str = Field(min_length=2, max_length=100)
    role: Literal["employee", "agent", "admin"]
    department: Department | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def validate_department(self):
        if self.role == "agent" and self.department is None:
            raise ValueError("Agents must belong to a supported service department")
        if self.role != "agent" and self.department is not None:
            raise ValueError("Only agents have a service department")
        return self

class CreateAccount(AccountInput):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.lower().strip()
        if " " in value or value.count("@") != 1 or not all(value.split("@")) or "." not in value.split("@")[1]:
            raise ValueError("A valid email is required")
        return value

class ResetPassword(BaseModel):
    password: str = Field(min_length=10, max_length=128)

class CategoryInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    label: str = Field(min_length=2, max_length=100)
    description: str = Field(max_length=500)
    is_active: bool

def account_data(user):
    return {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role, "department": user.department, "is_active": user.is_active}

@router.get("/branding")
def public_branding(db: Session = Depends(get_db)):
    return {"organization_name": settings_data(db)["organization_name"]}

@router.get("/settings")
def workspace_settings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return settings_data(db)

@router.put("/admin/settings")
def update_settings(payload: SettingsInput, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    before = settings_data(db)
    row = db.scalar(select(SystemSettings).where(SystemSettings.id == 1).with_for_update())
    if row is None:
        row = SystemSettings(id=1, **payload.model_dump())
        db.add(row)
    else:
        for key, value in payload.model_dump().items():
            setattr(row, key, value)
    if before != payload.model_dump():
        audit(db, actor, "settings.updated", "system", {"before": before, "after": payload.model_dump()})
    publish(db, "workspace.updated")
    db.commit()
    return settings_data(db)

@router.get("/admin/users")
def list_users(actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [account_data(user) for user in db.scalars(select(User).order_by(User.id)).all()]

@router.post("/admin/users", status_code=201)
def create_user(payload: CreateAccount, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "Email already exists")
    data = payload.model_dump(exclude={"password"})
    user = User(**data, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.flush()
        audit(db, actor, "user.created", f"user:{user.id}", data)
        publish(db, "workspace.updated")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already exists")
    return account_data(user)

@router.put("/admin/users/{user_id}")
def update_user(user_id: int, payload: AccountInput, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    # Serializes privilege changes so concurrent requests cannot remove all admins.
    admins = db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True)).order_by(User.id).with_for_update()).all()
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == actor.id and (payload.role != "admin" or not payload.is_active):
        raise HTTPException(409, "You cannot disable or demote your own admin account")
    if user.role == "admin" and user.is_active and (payload.role != "admin" or not payload.is_active) and len(admins) <= 1:
        raise HTTPException(409, "At least one active admin must remain")
    if (user.role, user.department, user.is_active) != (payload.role, payload.department, payload.is_active):
        assigned = db.scalar(select(Ticket.id).where(Ticket.assignee_id == user.id, Ticket.status != "Done"))
        if assigned is not None:
            raise HTTPException(409, "Reassign unfinished tickets before changing this account's access")
        user.token_version += 1
    before = account_data(user)
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    after = account_data(user)
    if before != after:
        audit(db, actor, "user.updated", f"user:{user.id}", {"before": before, "after": after})
    publish(db, "workspace.updated")
    db.commit()
    return after

@router.post("/admin/users/{user_id}/reset-password")
def reset_password(user_id: int, payload: ResetPassword, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == actor.id:
        raise HTTPException(409, "Use another admin to reset your own account")
    user.password_hash = hash_password(payload.password)
    user.token_version += 1
    audit(db, actor, "user.password_reset", f"user:{user.id}", {"email": user.email, "sessions_revoked": True})
    publish(db, "workspace.updated")
    db.commit()
    return {"ok": True}

@router.get("/admin/catalog")
def admin_catalog(actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    return catalog_data(db)

@router.put("/admin/catalog/{category}")
def update_category(category: Department, payload: CategoryInput, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    before = next(item for item in catalog_data(db) if item["category"] == category)
    row = db.get(ServiceCategory, category)
    if row is None:
        row = ServiceCategory(category=category, **payload.model_dump())
        db.add(row)
    else:
        for key, value in payload.model_dump().items():
            setattr(row, key, value)
    after = {"category": category, "department": category, **payload.model_dump()}
    if before != after:
        audit(db, actor, "catalog.updated", category, {"before": before, "after": after})
    publish(db, "workspace.updated")
    db.commit()
    return after

@router.get("/admin/audit")
def list_audit(actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(AdminAudit).options(selectinload(AdminAudit.actor)).order_by(AdminAudit.id.desc()).limit(200)).all()
    return [{"id": row.id, "actor_email": row.actor.email, "action": row.action, "target": row.target, "details": row.details, "created_at": row.created_at} for row in rows]

@router.get("/admin/overview")
def overview(actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    tickets = db.scalars(select(Ticket)).all()
    now = datetime.now(timezone.utc)
    threshold = settings_data(db)["aging_hours"]
    def utc(value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    unfinished = [t for t in tickets if t.status != "Done"]
    days = [(now - timedelta(days=i)).date() for i in range(6, -1, -1)]
    return {
        "total": len(tickets), "open": sum(t.status == "Open" for t in tickets),
        "in_progress": sum(t.status == "In Progress" for t in tickets), "done": sum(t.status == "Done" for t in tickets),
        "urgent": sum(t.priority == "Urgent" for t in unfinished), "unassigned": sum(t.assignee_id is None for t in unfinished),
        "aging": sum((now - utc(t.created_at)).total_seconds() >= threshold * 3600 for t in unfinished),
        "aging_hours": threshold,
        "by_department": [{"department": dept, "total": sum(t.department == dept for t in tickets), "open": sum(t.department == dept and t.status != "Done" for t in tickets), "done": sum(t.department == dept and t.status == "Done" for t in tickets)} for dept in DEPARTMENT_CODES],
        "daily": [{"date": str(day), "count": sum(utc(t.created_at).date() == day for t in tickets)} for day in days],
        "active_users": len(db.scalars(select(User).where(User.is_active.is_(True))).all()),
    }
