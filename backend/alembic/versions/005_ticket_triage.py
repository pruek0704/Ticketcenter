"""Add impact details and audited priority triage.

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tickets", sa.Column("impact", sa.Text(), server_default="", nullable=False))
    op.create_table(
        "ticket_priority_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_priority", sa.String(length=16), nullable=False),
        sa.Column("to_priority", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ticket_priority_history_ticket_id", "ticket_priority_history", ["ticket_id"])


def downgrade():
    op.drop_index("ix_ticket_priority_history_ticket_id", table_name="ticket_priority_history")
    op.drop_table("ticket_priority_history")
    op.drop_column("tickets", "impact")
