from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('employee','agent','admin')", name="user_role"),
        CheckConstraint("department IS NULL OR department IN ('IT','HR','FAC','FIN','PROC')", name="user_department"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16))
    department: Mapped[str | None] = mapped_column(String(16), nullable=True)
    display_name: Mapped[str] = mapped_column(String(100), default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    token_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("category IN ('IT','HR','FAC','FIN','PROC')", name="ticket_category"),
        CheckConstraint("department IN ('IT','HR','FAC','FIN','PROC')", name="ticket_department"),
        CheckConstraint("status IN ('Open','In Progress','Done')", name="ticket_status"),
        CheckConstraint("priority IN ('Normal','Urgent')", name="ticket_priority"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    impact: Mapped[str] = mapped_column(Text, default="", server_default="")
    category: Mapped[str] = mapped_column(String(16))
    department: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="Open")
    priority: Mapped[str] = mapped_column(String(16), default="Normal", server_default="Normal")
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[User | None] = relationship(foreign_keys=[assignee_id])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    history: Mapped[list["TicketHistory"]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketHistory.id")
    messages: Mapped[list["TicketMessage"]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.id")
    priority_history: Mapped[list["TicketPriorityHistory"]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketPriorityHistory.id")

    @property
    def assignee_name(self) -> str | None:
        return (self.assignee.display_name or self.assignee.email) if self.assignee else None

class TicketHistory(Base):
    __tablename__ = "ticket_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ticket: Mapped[Ticket] = relationship(back_populates="history")
    actor: Mapped[User] = relationship(foreign_keys=[actor_id])

    @property
    def actor_email(self) -> str:
        return self.actor.email if self.actor else f"User #{self.actor_id}"

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String(100), default="บริษัท ตัวอย่าง จำกัด")
    announcement: Mapped[str] = mapped_column(Text, default="")
    accepting_tickets: Mapped[bool] = mapped_column(Boolean, default=True)
    aging_hours: Mapped[int] = mapped_column(Integer, default=24)

class ServiceCategory(Base):
    __tablename__ = "service_categories"
    category: Mapped[str] = mapped_column(String(16), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class AdminAudit(Base):
    __tablename__ = "admin_audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor: Mapped[User] = relationship(foreign_keys=[actor_id])

class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ticket: Mapped[Ticket] = relationship(back_populates="messages")
    author: Mapped[User] = relationship(foreign_keys=[author_id])

    @property
    def author_email(self) -> str:
        return self.author.email if self.author else f"User #{self.author_id}"

    @property
    def author_role(self) -> str:
        return self.author.role if self.author else "unknown"

class TicketRead(Base):
    __tablename__ = "ticket_reads"
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    last_read_message_id: Mapped[int | None] = mapped_column(ForeignKey("ticket_messages.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TicketPriorityHistory(Base):
    __tablename__ = "ticket_priority_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    from_priority: Mapped[str] = mapped_column(String(16))
    to_priority: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ticket: Mapped[Ticket] = relationship(back_populates="priority_history")
    actor: Mapped[User] = relationship(foreign_keys=[actor_id])

    @property
    def actor_email(self) -> str:
        return self.actor.email if self.actor else f"User #{self.actor_id}"
