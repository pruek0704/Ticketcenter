"""Extend queues to facilities, finance and procurement without replacing existing work."""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None

def constraints(codes):
    values = ",".join(repr(code) for code in codes)
    for table, name, expression in [
        ("users", "user_department", f"department IS NULL OR department IN ({values})"),
        ("tickets", "ticket_category", f"category IN ({values})"),
        ("tickets", "ticket_department", f"department IN ({values})"),
    ]:
        op.drop_constraint(name, table, type_="check")
        op.create_check_constraint(name, table, expression)

def upgrade():
    constraints(("IT", "HR", "FAC", "FIN", "PROC"))
    table = sa.table("service_categories", sa.column("category", sa.String), sa.column("label", sa.String), sa.column("description", sa.String), sa.column("is_active", sa.Boolean))
    op.bulk_insert(table, [
        {"category": "FAC", "label": "อาคารและสถานที่ / ธุรการ", "description": "แอร์ ไฟ ห้องประชุม เฟอร์นิเจอร์ และพื้นที่สำนักงาน", "is_active": True},
        {"category": "FIN", "label": "การเงินและบัญชี", "description": "เบิกค่าใช้จ่าย เอกสารภาษี และติดตามการชำระเงิน", "is_active": True},
        {"category": "PROC", "label": "จัดซื้อ", "description": "ขอซื้ออุปกรณ์สำนักงาน ติดตามคำขอซื้อ และข้อมูลผู้ขาย", "is_active": True},
    ])

def downgrade():
    connection = op.get_bind()
    if connection.scalar(sa.text("SELECT count(*) FROM tickets WHERE department NOT IN ('IT','HR')")) or connection.scalar(sa.text("SELECT count(*) FROM users WHERE department NOT IN ('IT','HR')")):
        raise RuntimeError("Cannot remove departments while tickets or agents use them. Preserve or reassign the data first.")
    connection.execute(sa.text("DELETE FROM service_categories WHERE category IN ('FAC','FIN','PROC')"))
    constraints(("IT", "HR"))
