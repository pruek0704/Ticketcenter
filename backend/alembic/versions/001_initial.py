"""Initial TicketCenter schema.

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("department", sa.String(16)),
        sa.CheckConstraint("role IN ('employee','agent','admin')", name="user_role"),
        sa.CheckConstraint("department IS NULL OR department IN ('IT','HR')", name="user_department"))
    op.create_table("tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(16), nullable=False),
        sa.Column("department", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="Open"),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("category IN ('IT','HR')", name="ticket_category"),
        sa.CheckConstraint("department IN ('IT','HR')", name="ticket_department"),
        sa.CheckConstraint("status IN ('Open','In Progress','Done')", name="ticket_status"))
    op.create_index("ix_tickets_employee", "tickets", ["employee_id"])
    op.create_index("ix_tickets_department", "tickets", ["department"])
    op.create_table("ticket_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_status", sa.String(16)),
        sa.Column("to_status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

def downgrade():
    op.drop_table("ticket_history")
    op.drop_index("ix_tickets_department", table_name="tickets")
    op.drop_index("ix_tickets_employee", table_name="tickets")
    op.drop_table("tickets")
    op.drop_table("users")
