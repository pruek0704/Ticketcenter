"""Add validated priority to tickets.

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("tickets", sa.Column("priority", sa.String(16), nullable=False, server_default="Normal"))
    op.create_check_constraint("ticket_priority", "tickets", "priority IN ('Normal','Urgent')")

def downgrade():
    op.drop_constraint("ticket_priority", "tickets", type_="check")
    op.drop_column("tickets", "priority")
