from datetime import datetime
from typing import Literal
import os
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload
from .auth import bearer, create_token, current_user, verify_password
from .db import get_db
from .models import Ticket, TicketHistory, TicketMessage, TicketPriorityHistory, TicketRead, User
from .admin import router as admin_router, catalog_data, settings_data, audit, require_admin
from .departments import Department, DEPARTMENT_CODES, DEPARTMENT_NAMES
from .realtime import publish, stream_events

app = FastAPI(title="TicketCenter API", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.include_router(admin_router)
Category = Department
Status = Literal["Open", "In Progress", "Done"]
Priority = Literal["Normal", "Urgent"]

class LoginInput(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    department: str | None
    display_name: str
    is_active: bool

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TicketInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=3, max_length=5000)
    impact: str = Field(min_length=3, max_length=2000)
    category: Category

    @model_validator(mode="before")
    @classmethod
    def priority_is_assigned_by_service_team(cls, values):
        if isinstance(values, dict) and "priority" in values:
            raise ValueError("Priority is assigned by the service team")
        return values

class StatusInput(BaseModel):
    status: Status

class PriorityInput(BaseModel):
    priority: Priority

class MessageInput(BaseModel):
    body: str = Field(min_length=1, max_length=4000)

class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    actor_id: int
    actor_email: str
    from_status: str | None
    to_status: str
    created_at: datetime

class PriorityHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    actor_id: int
    actor_email: str
    from_priority: str
    to_priority: str
    created_at: datetime

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    impact: str
    category: str
    department: str
    status: str
    priority: str
    employee_id: int
    assignee_id: int | None
    assignee_name: str | None
    created_at: datetime
    history: list[HistoryOut]
    priority_history: list[PriorityHistoryOut]

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    author_id: int
    author_email: str
    author_role: str
    body: str
    created_at: datetime

def visible(ticket: Ticket, user: User) -> bool:
    return user.role == "admin" or (user.role == "employee" and ticket.employee_id == user.id) or (user.role == "agent" and ticket.department == user.department)

def get_visible_ticket(ticket_id: int, user: User, db: Session) -> Ticket:
    ticket = db.scalar(select(Ticket).options(selectinload(Ticket.history).selectinload(TicketHistory.actor), selectinload(Ticket.priority_history).selectinload(TicketPriorityHistory.actor)).where(Ticket.id == ticket_id))
    if ticket is None or not visible(ticket, user):
        raise HTTPException(404, "Ticket not found")
    return ticket

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/departments")
def departments():
    return [{"code": code, "name": name} for code, name in DEPARTMENT_NAMES.items()]

@app.get("/api/events")
def events(request: Request, user: User = Depends(current_user), credentials=Depends(bearer), db: Session = Depends(get_db)):
    if db.get_bind().dialect.name != "postgresql":
        raise HTTPException(503, "Realtime requires PostgreSQL")
    try:
        token_data = jwt.decode(credentials.credentials, os.environ["JWT_SECRET"], algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    user_id, version, expires = user.id, user.token_version, token_data["exp"]
    dsn = db.get_bind().url.render_as_string(hide_password=False).replace("postgresql+psycopg://", "postgresql://")
    db.close()  # Do not hold the REST pool transaction open for a long-lived stream.
    return StreamingResponse(stream_events(dsn, user_id, version, expires, request), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/api/catalog")
def catalog(db: Session = Depends(get_db)):
    return [item for item in catalog_data(db) if item["is_active"]]

@app.post("/api/login", response_model=LoginOut)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return LoginOut(access_token=create_token(user), user=UserOut.model_validate(user))

@app.get("/api/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user

@app.post("/api/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "employee":
        raise HTTPException(403, "Only employees can create tickets")
    if not settings_data(db)["accepting_tickets"]:
        raise HTTPException(409, "New requests are temporarily paused")
    service = next((item for item in catalog_data(db) if item["category"] == payload.category and item["is_active"]), None)
    if not service:
        raise HTTPException(409, "This service is temporarily unavailable")
    # The backend derives the queue. A caller cannot submit a department field.
    ticket = Ticket(title=payload.title.strip(), description=payload.description.strip(), impact=payload.impact.strip(), category=payload.category, department=payload.category, status="Open", priority="Normal", employee_id=user.id)
    db.add(ticket)
    db.flush()
    db.add(TicketHistory(ticket_id=ticket.id, actor_id=user.id, from_status=None, to_status="Open"))
    publish(db, "ticket.updated", ticket=ticket)
    db.commit()
    return get_visible_ticket(ticket.id, user, db)

@app.get("/api/tickets", response_model=list[TicketOut])
def list_tickets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Ticket).options(selectinload(Ticket.history).selectinload(TicketHistory.actor), selectinload(Ticket.priority_history).selectinload(TicketPriorityHistory.actor)).order_by(Ticket.id.desc())
    if user.role == "employee":
        query = query.where(Ticket.employee_id == user.id)
    elif user.role == "agent":
        query = query.where(Ticket.department == user.department)
    return db.scalars(query).all()

@app.get("/api/tickets/{ticket_id}", response_model=TicketOut)
def ticket_detail(ticket_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_visible_ticket(ticket_id, user, db)

@app.get("/api/tickets/{ticket_id}/messages", response_model=list[MessageOut])
def list_ticket_messages(ticket_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_visible_ticket(ticket_id, user, db)
    messages = db.scalars(
        select(TicketMessage)
        .options(selectinload(TicketMessage.author))
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.id)
    )
    return messages.all()

@app.post("/api/tickets/{ticket_id}/messages", response_model=MessageOut, status_code=201)
def create_ticket_message(ticket_id: int, payload: MessageInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_visible_ticket(ticket_id, user, db)
    body = payload.body.strip()
    if not body:
        raise HTTPException(422, "Message cannot be empty")
    message = TicketMessage(ticket_id=ticket_id, author_id=user.id, body=body)
    db.add(message)
    db.flush()
    publish(db, "message.created", ticket=db.get(Ticket, ticket_id), message=message)
    db.commit()
    return db.scalar(
        select(TicketMessage)
        .options(selectinload(TicketMessage.author))
        .where(TicketMessage.id == message.id)
    )

@app.post("/api/tickets/{ticket_id}/messages/read")
def mark_ticket_messages_read(ticket_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = get_visible_ticket(ticket_id, user, db)
    latest_id = db.scalar(select(func.max(TicketMessage.id)).where(TicketMessage.ticket_id == ticket_id))
    if latest_id is None:
        return {"ticket_id": ticket_id, "unread": 0}
    read_state = db.get(TicketRead, (ticket_id, user.id))
    changed = False
    if read_state is None:
        read_state = TicketRead(ticket_id=ticket_id, user_id=user.id, last_read_message_id=latest_id)
        db.add(read_state)
        changed = True
    elif read_state.last_read_message_id is None or latest_id > read_state.last_read_message_id:
        read_state.last_read_message_id = latest_id
        changed = True
    if changed:
        publish(db, "read.updated", ticket=ticket)
    db.commit()
    return {"ticket_id": ticket_id, "unread": 0}

@app.get("/api/unread-counts")
def unread_message_counts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = (
        select(TicketMessage.ticket_id, func.count(TicketMessage.id))
        .join(Ticket, Ticket.id == TicketMessage.ticket_id)
        .outerjoin(TicketRead, and_(TicketRead.ticket_id == TicketMessage.ticket_id, TicketRead.user_id == user.id))
        .where(
            TicketMessage.author_id != user.id,
            or_(TicketRead.last_read_message_id.is_(None), TicketMessage.id > TicketRead.last_read_message_id),
        )
        .group_by(TicketMessage.ticket_id)
    )
    if user.role == "employee":
        query = query.where(Ticket.employee_id == user.id)
    elif user.role == "agent":
        query = query.where(Ticket.department == user.department)
    return {str(ticket_id): count for ticket_id, count in db.execute(query).all()}

@app.patch("/api/tickets/{ticket_id}/status", response_model=TicketOut)
def update_status(ticket_id: int, payload: StatusInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ("agent", "admin"):
        raise HTTPException(403, "Only agents or admins can update status")
    ticket = get_visible_ticket(ticket_id, user, db)
    next_status = {"Open": "In Progress", "In Progress": "Done"}.get(ticket.status)
    if payload.status != next_status:
        raise HTTPException(409, "Status must move Open → In Progress → Done")
    old = ticket.status
    ticket.status = payload.status
    db.add(TicketHistory(ticket_id=ticket.id, actor_id=user.id, from_status=old, to_status=payload.status))
    publish(db, "ticket.updated", ticket=ticket)
    db.commit()
    return get_visible_ticket(ticket.id, user, db)

@app.patch("/api/tickets/{ticket_id}/priority", response_model=TicketOut)
def update_priority(ticket_id: int, payload: PriorityInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ("agent", "admin"):
        raise HTTPException(403, "Only agents or admins can set priority")
    ticket = get_visible_ticket(ticket_id, user, db)
    if ticket.priority == payload.priority:
        return ticket
    old_priority = ticket.priority
    ticket.priority = payload.priority
    db.add(TicketPriorityHistory(ticket_id=ticket.id, actor_id=user.id, from_priority=old_priority, to_priority=payload.priority))
    publish(db, "ticket.updated", ticket=ticket)
    db.commit()
    return get_visible_ticket(ticket.id, user, db)

@app.get("/api/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Ticket.department, func.count(Ticket.id)).group_by(Ticket.department)
    if user.role == "employee":
        query = query.where(Ticket.employee_id == user.id)
    elif user.role == "agent":
        query = query.where(Ticket.department == user.department)
    counts = dict(db.execute(query).all())
    return {"total": sum(counts.values()), "by_department": {code: counts.get(code, 0) for code in DEPARTMENT_CODES}}

class AssignmentInput(BaseModel):
    assignee_id: int | None = None

@app.patch("/api/admin/tickets/{ticket_id}/assignee", response_model=TicketOut)
def assign_ticket(ticket_id: int, payload: AssignmentInput, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ticket = get_visible_ticket(ticket_id, user, db)
    if ticket.status == "Done":
        raise HTTPException(409, "Completed tickets cannot be reassigned")
    agent = db.get(User, payload.assignee_id) if payload.assignee_id is not None else None
    if payload.assignee_id is not None and (not agent or not agent.is_active or agent.role != "agent" or agent.department != ticket.department):
        raise HTTPException(422, "Choose an active agent from the ticket's department")
    if ticket.assignee_id != payload.assignee_id:
        audit(db, user, "ticket.assigned", f"ticket:{ticket.id}", {"before": ticket.assignee_id, "after": payload.assignee_id, "agent_email": agent.email if agent else None})
        ticket.assignee_id = payload.assignee_id
        publish(db, "ticket.updated", ticket=ticket)
        db.commit()
    return get_visible_ticket(ticket.id, user, db)
