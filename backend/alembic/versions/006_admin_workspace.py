"""Admin workspace, account controls, service settings and assignments."""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("display_name", sa.String(100), nullable=False, server_default=""))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("tickets", sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    settings = op.create_table("system_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_name", sa.String(100), nullable=False),
        sa.Column("announcement", sa.Text(), nullable=False),
        sa.Column("accepting_tickets", sa.Boolean(), nullable=False),
        sa.Column("aging_hours", sa.Integer(), nullable=False))
    op.bulk_insert(settings, [{"id": 1, "organization_name": "บริษัท ตัวอย่าง จำกัด", "announcement": "", "accepting_tickets": True, "aging_hours": 24}])
    categories = op.create_table("service_categories",
        sa.Column("category", sa.String(16), primary_key=True),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False))
    op.bulk_insert(categories, [
        {"category": "IT", "label": "IT Support", "description": "คอมพิวเตอร์ เครือข่าย และระบบงาน", "is_active": True},
        {"category": "HR", "label": "HR Services", "description": "วันลา สวัสดิการ และข้อมูลพนักงาน", "is_active": True}])
    op.create_table("admin_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("target", sa.String(100), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

def downgrade():
    op.drop_table("admin_audit")
    op.drop_table("service_categories")
    op.drop_table("system_settings")
    op.drop_column("tickets", "assignee_id")
    op.drop_column("users", "token_version")
    op.drop_column("users", "is_active")
    op.drop_column("users", "display_name")
