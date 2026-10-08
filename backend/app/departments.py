"""Supported service queues. Category validation and routing share this definition."""
from typing import Literal

Department = Literal["IT", "HR", "FAC", "FIN", "PROC"]
DEPARTMENT_NAMES = {
    "IT": "ฝ่ายเทคโนโลยีสารสนเทศ (IT)",
    "HR": "ฝ่ายทรัพยากรบุคคล (HR)",
    "FAC": "ฝ่ายอาคารและสถานที่ / ธุรการ",
    "FIN": "ฝ่ายการเงินและบัญชี",
    "PROC": "ฝ่ายจัดซื้อ",
}
DEPARTMENT_CODES = tuple(DEPARTMENT_NAMES)
DEFAULT_CATALOG = [
    {"category": "IT", "label": "IT Support", "description": "คอมพิวเตอร์ เครือข่าย และระบบงาน", "is_active": True},
    {"category": "HR", "label": "HR Services", "description": "วันลา สวัสดิการ และข้อมูลพนักงาน", "is_active": True},
    {"category": "FAC", "label": "อาคารและสถานที่ / ธุรการ", "description": "แอร์ ไฟ ห้องประชุม เฟอร์นิเจอร์ และพื้นที่สำนักงาน", "is_active": True},
    {"category": "FIN", "label": "การเงินและบัญชี", "description": "เบิกค่าใช้จ่าย เอกสารภาษี และติดตามการชำระเงิน", "is_active": True},
    {"category": "PROC", "label": "จัดซื้อ", "description": "ขอซื้ออุปกรณ์สำนักงาน ติดตามคำขอซื้อ และข้อมูลผู้ขาย", "is_active": True},
]
