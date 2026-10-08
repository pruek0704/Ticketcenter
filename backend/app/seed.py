import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import hash_password
from .db import engine
from .models import Ticket, TicketHistory, TicketPriorityHistory, User

def main():
    if os.environ.get("DEMO_SEED", "false").lower() != "true":
        return
    accounts = [
        ("employee@example.test", "employee", None, "DEMO_EMPLOYEE_PASSWORD"),
        ("it.agent@example.test", "agent", "IT", "DEMO_IT_PASSWORD"),
        ("hr.agent@example.test", "agent", "HR", "DEMO_HR_PASSWORD"),
        ("admin@example.test", "admin", None, "DEMO_ADMIN_PASSWORD"),
        ("fac.agent@example.test", "agent", "FAC", "DEMO_FAC_PASSWORD"),
        ("fin.agent@example.test", "agent", "FIN", "DEMO_FIN_PASSWORD"),
        ("proc.agent@example.test", "agent", "PROC", "DEMO_PROC_PASSWORD"),
    ]
    with Session(engine) as db:
        for email, role, department, env_name in accounts:
            password = os.environ.get(env_name)
            if not password:
                continue
            if not db.scalar(select(User).where(User.email == email)):
                db.add(User(email=email, role=role, department=department, password_hash=hash_password(password)))
        db.commit()
        employee = db.scalar(select(User).where(User.email == "employee@example.test"))
        it_agent = db.scalar(select(User).where(User.email == "it.agent@example.test"))
        hr_agent = db.scalar(select(User).where(User.email == "hr.agent@example.test"))
        if not employee or not it_agent or not hr_agent:
            return
        samples = [
            ("ตัวอย่าง: โน้ตบุ๊กเปิดไม่ติด", "เครื่องทำงานเปิดไม่ติดหลังอัปเดตระบบ", "พนักงานหนึ่งคนใช้งานอุปกรณ์หลักไม่ได้และมีประชุมสำคัญในช่วงบ่าย", "IT", "Open", "Urgent", it_agent.id),
            ("ตัวอย่าง: สอบถามสิทธิวันลา", "ขอตรวจสอบวันลาคงเหลือก่อนวางแผนวันหยุด", "ยังปฏิบัติงานได้ตามปกติ ต้องการข้อมูลเพื่อวางแผนวันหยุด", "HR", "In Progress", "Normal", hr_agent.id),
            ("ตัวอย่าง: แอร์ห้องประชุมไม่เย็น", "แอร์ห้องประชุมชั้นสองไม่เย็น", "ห้องประชุมใช้งานไม่สะดวก มีประชุมช่วงบ่าย", "FAC", "Open", "Normal", employee.id),
            ("ตัวอย่าง: ติดตามเบิกค่าเดินทาง", "ขอตรวจสอบสถานะการเบิกค่าเดินทางที่ส่งเอกสารแล้ว", "พนักงานต้องการทราบวันรับเงินเพื่อวางแผนค่าใช้จ่าย", "FIN", "Open", "Normal", employee.id),
            ("ตัวอย่าง: ขอซื้ออุปกรณ์สำนักงาน", "ต้องการซื้อเก้าอี้สำนักงานทดแทนตัวที่ชำรุด", "หนึ่งที่นั่งทำงานได้ไม่สะดวก ขอให้ทีมจัดซื้อประเมิน", "PROC", "Open", "Normal", employee.id),
        ]
        for title, description, impact, category, status, priority, actor_id in samples:
            existing = db.scalar(select(Ticket).where(Ticket.title == title, Ticket.employee_id == employee.id))
            if existing:
                if not existing.impact:
                    existing.impact = impact
                continue
            ticket = Ticket(title=title, description=description, impact=impact, category=category, department=category, status="Open", priority="Normal", employee_id=employee.id)
            db.add(ticket)
            db.flush()
            db.add(TicketHistory(ticket_id=ticket.id, actor_id=employee.id, from_status=None, to_status="Open"))
            if priority != "Normal":
                ticket.priority = priority
                db.add(TicketPriorityHistory(ticket_id=ticket.id, actor_id=actor_id, from_priority="Normal", to_priority=priority))
            if status != "Open":
                ticket.status = status
                db.add(TicketHistory(ticket_id=ticket.id, actor_id=actor_id, from_status="Open", to_status=status))
        db.commit()

if __name__ == "__main__":
    main()
