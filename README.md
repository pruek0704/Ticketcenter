# TicketCenter MVP

ระบบจัดการคำขอบริการภายในองค์กร ช่วยให้พนักงานแจ้งปัญหา ติดตามสถานะ และคุยกับเจ้าหน้าที่ในที่เดียว ส่วนเจ้าหน้าที่มีคิวงานของฝ่ายตนเพื่อรับงานและอัปเดตความคืบหน้า

รองรับ **5 ฝ่าย**: เทคโนโลยีสารสนเทศ (IT), ทรัพยากรบุคคล (HR), อาคารและสถานที่/ธุรการ (FAC), การเงินและบัญชี (FIN) และจัดซื้อ (PROC)

## บทบาทผู้ใช้งาน

| บทบาท | สิ่งที่ทำได้ |
|---|---|
| **Employee — พนักงาน** | สร้างคำขอ อธิบายผลกระทบ ดูสถานะและประวัติของคำขอตนเอง และคุยกับเจ้าหน้าที่ |
| **Agent — เจ้าหน้าที่** | ดูคิวเฉพาะฝ่าย รับงาน ประเมินความเร่งด่วน เปลี่ยนสถานะ และตอบข้อความพนักงาน |
| **Admin — ผู้ดูแลระบบ** | ดูงานทุกฝ่าย มอบหมายงาน จัดการผู้ใช้และสิทธิ์ หมวดบริการ การตั้งค่าระบบ และประวัติการจัดการ |

## ฟีเจอร์หลัก

- **ส่งคำขอเข้าฝ่ายที่รับผิดชอบ** — Backend ตรวจหมวดบริการและกำหนดคิวให้โดยอัตโนมัติ
- **ติดตามสถานะงาน** — Open → In Progress → Done พร้อมไทม์ไลน์ว่าใครดำเนินการและเมื่อไร
- **ประเมินความเร่งด่วนโดยเจ้าหน้าที่** — คำขอใหม่เริ่มเป็นปกติ Agent ปรับได้เฉพาะฝ่ายตน ส่วน Admin ปรับได้ทุกฝ่าย พร้อมบันทึกประวัติ
- **แชทภายใน Ticket แบบทันที** — ข้อความปรากฏข้ามบัญชีโดยไม่ต้องรีเฟรช พร้อมจำนวนข้อความที่ยังไม่อ่านและการเชื่อมต่อใหม่เมื่อเครือข่ายกลับมา
- **ค้นหาและจัดลำดับงาน** — ค้นด้วยหัวข้อหรือเลข Ticket กรองตามสถานะ/ฝ่าย และแสดงงานเร่งด่วนก่อนในคิวเจ้าหน้าที่
- **Dashboard และพื้นที่ Admin** — สรุปงานตามสถานะและฝ่าย พร้อมเครื่องมือจัดการระบบ
- **หน้าจอที่อ่านง่าย** — รองรับธีมสว่าง/มืด มือถือ และการขยายพื้นที่ทำงาน

ข้อมูลและข้อความถูกตรวจสิทธิ์ที่ Backend ทุกครั้ง การแจ้งเตือนแบบ push เป็นฟีเจอร์สำหรับพัฒนาต่อ

## เทคโนโลยี

| เครื่องมือ | หน้าที่ |
|---|---|
| React + Vite | หน้าเว็บแบบโต้ตอบและ build ไฟล์เว็บสำหรับให้บริการ |
| Nginx | ให้บริการหน้าเว็บ รับ HTTPS และส่งคำขอ `/api` ไป Backend |
| FastAPI + SQLAlchemy | REST API ตรวจสิทธิ์และจัดการข้อมูล |
| PostgreSQL | เก็บผู้ใช้ Ticket ข้อความและประวัติ รวมถึงส่ง event สำหรับแชทแบบทันที |
| Alembic | จัดการเวอร์ชันและ migration ของ schema ฐานข้อมูล |
| Docker Compose | รันบริการสำหรับพัฒนาและทดสอบบนเครื่อง |
| Terraform | ตัวอย่าง Infrastructure as Code สำหรับ AWS |

## สถานะการ deploy บน Cloud Lab

แยก Web ไว้ใน public subnet และ API/ฐานข้อมูลไว้ใน private subnet เปิดหน้าเว็บผ่าน HTTPS และทดสอบ Employee login ได้แล้ว ปัจจุบันใช้ Bastion เป็น TCP relay ชั่วคราว เนื่องจากเส้นทางตรงระหว่าง subnet และการ apply Firewall ของ Lab มีปัญหา:

```text
Browser → Nginx → Bastion relay → FastAPI → PostgreSQL
```

สิ่งที่ยังต้องตรวจรับคือเดโมครบวงจร การจำกัด Firewall และทดสอบการเข้าถึงที่ต้องถูกบล็อก การเริ่มบริการหลัง instance restart และทางเข้า HTTPS/certificate ให้ตรงเกณฑ์อาจารย์ ปัจจุบันพอร์ตภายนอกเป็น `11101` และ certificate เป็น self-signed จึงยังไม่ถือว่าการ deploy และ Security ผ่านครบทุกข้อ

## โครงสร้าง

```text
frontend/       React + Vite, Nginx (HTTPS และ reverse proxy /api)
backend/        FastAPI, SQLAlchemy, Alembic migration, tests
infra/aws/      Terraform: VPC, public/private subnets, ALB, ECS, RDS, security groups
docs/           แผนภาพ รายงาน และสไลด์สำหรับนำเสนอ
compose.yaml    สภาพแวดล้อมพัฒนาในเครื่อง
.env.example    ตัวอย่างตัวแปรแวดล้อม ไม่มี secret จริง
```

แผนภาพ System Flow, AWS/Compose Architecture, Business Flow และ Data Flow ดูได้ที่ [docs/ticketcenter-flows.md](docs/ticketcenter-flows.md).
รายงาน Word ที่รวมคำอธิบายและแผนภาพสำหรับนำเสนอ ดูได้ที่ [docs/TicketCenter_Architecture_Report.docx](docs/TicketCenter_Architecture_Report.docx).

ไฟล์ใน `infra/aws/` เป็นตัวอย่างสำหรับ AWS ไม่ใช่การตั้งค่าที่ deploy บน Cloud Lab ปัจจุบัน และ Docker Compose บนเครื่องไม่ได้เป็นหลักฐานว่ามี public/private subnet จริง การทดสอบ API บางส่วนใช้ SQLite ชั่วคราว ส่วนการทดสอบแชทแบบทันทีใช้ PostgreSQL จริง

## รันบนเครื่องด้วย Docker Compose

ต้องมี Docker Engine พร้อม Compose. คัดลอก `.env.example` เป็น `.env` แล้วเปลี่ยน `POSTGRES_PASSWORD`, `JWT_SECRET` (อย่างน้อย 32 ตัวอักษร) และรหัสผ่านเดโมทั้งสี่ให้เป็นค่าที่คาดเดายาก. `.env` ถูก ignore โดย Git. จากโฟลเดอร์ราก:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

เปิด `https://localhost` และยอมรับ self-signed certificate สำหรับ **เดโมในเครื่องเท่านั้น**. Port 80 ใช้ redirect ไป 443. มีเพียงบริการ `web` ที่ publish port; `api` และ `db` ไม่มี port ที่เปิดออก host. ข้อมูล PostgreSQL อยู่ใน volume `pgdata`.

บัญชีเดโมที่สร้างเมื่อ `DEMO_SEED=true` (ใช้รหัสผ่านตาม `.env`):

| บัญชี | บทบาท |
|---|---|
| `employee@example.test` | Employee |
| `it.agent@example.test` | Agent ฝ่าย IT |
| `hr.agent@example.test` | Agent ฝ่าย HR |
| `admin@example.test` | Admin |

ข้อมูล Ticket ตัวอย่างครอบคลุมทั้ง 5 ฝ่ายจะถูกสร้างให้ Employee ด้วย Seed เรียกซ้ำได้ โดยเพิ่มบัญชี/ตัวอย่างเฉพาะรายการที่ยังไม่มีอยู่ บัญชี Agent ของ FAC/FIN/PROC จะสร้างเมื่อกำหนดรหัสเดโมของฝ่ายนั้นไว้ รายละเอียดอยู่ในหัวข้อ “ฝ่ายบริการเพิ่มและแชทแบบทันที” ด้านล่าง

การ seed เพิ่มเฉพาะบัญชีที่ยังไม่มีอยู่และไม่เปลี่ยนรหัสผ่านของบัญชีเดิม. ถ้าต้องการรีเซ็ตข้อมูลเดโม ให้ใช้ `docker compose down -v` ซึ่ง **ลบข้อมูลใน volume** แล้วรันขึ้นใหม่.

## พื้นที่ Admin และหน้าตาใหม่ (Sprint 2)

Login ด้วย `admin@example.test` แล้วใช้เมนู “พื้นที่ผู้ดูแล”:

- **ภาพรวมองค์กร**: จำนวนงานตามสถานะ, งานเร่งด่วนที่ยังไม่เสร็จ, งานที่ยังไม่มอบหมาย, งานที่เปิดเกินเกณฑ์ และคำขอใหม่ใน 7 วัน (วันที่ UTC). คลิกตัวเลขในส่วนงานที่ควรดูแลเพื่อเปิดรายการที่กรองแล้ว.
- **ผู้ใช้และสิทธิ์**: เพิ่มบัญชีพนักงาน/เจ้าหน้าที่/Admin, แก้ชื่อและสิทธิ์, ระงับ/เปิดบัญชี และรีเซ็ตรหัสผ่าน (อย่างน้อย 10 ตัวอักษร). เจ้าหน้าที่ต้องอยู่ในหนึ่งใน 5 ฝ่ายบริการที่รองรับ. เปลี่ยนสิทธิ์ ระงับบัญชี และรีเซ็ตรหัสผ่านจะยกเลิกโทเคนเดิมทันที. Admin ปิดหรือลดสิทธิ์ตนเองไม่ได้ และระบบต้องมี Admin ที่เปิดใช้งานอย่างน้อยหนึ่งคน. หากเจ้าหน้าที่มีงานมอบหมายที่ยังไม่เสร็จ ต้องมอบหมายให้คนอื่นหรือยกเลิกการมอบหมายก่อนเปลี่ยนสิทธิ์.
- **หมวดบริการ**: เปลี่ยนชื่อและคำอธิบายบริการของทั้ง 5 ฝ่าย, เปิดหรือพักการรับคำขอใหม่ในแต่ละหมวด. งานเดิมยังอยู่และจัดการต่อได้; Backend ตรวจสถานะหมวดเมื่อสร้าง Ticket แม้ผู้ใช้เรียก API โดยตรง. คิว IT, HR, FAC, FIN และ PROC มีสิทธิ์แยกตามฝ่าย.
- **ตั้งค่าระบบ**: ชื่อองค์กร, ประกาศถึงผู้ใช้ที่ Login, เปิด/พักการรับคำขอทั้งระบบ และเกณฑ์เน้นงานค้าง 1–720 ชั่วโมง. เกณฑ์อายุงานเป็นสัญญาณเตือนภายใน ไม่ใช่ SLA และไม่ปรับ priority อัตโนมัติ.
- **ประวัติผู้ดูแล**: ดู/ค้นหาเหตุการณ์ล่าสุดสูงสุด 200 รายการ พร้อมผู้ทำ เวลา และรายละเอียดก่อน/หลัง. ไม่บันทึกรหัสผ่านหรือ password hash ใน audit.
- **มอบหมาย Ticket**: ในกล่องงาน Admin เลือกเจ้าหน้าที่ที่เปิดใช้งานในฝ่ายเดียวกับ Ticket และยืนยันก่อนบันทึก. Employee เห็นชื่อผู้รับผิดชอบ; Agent ในฝ่ายยังช่วยงานในคิวได้. งานที่ Done แล้วมอบหมายใหม่ไม่ได้.

ค่าระบบ หมวด ผู้ใช้ ผู้รับผิดชอบ และ audit เก็บใน PostgreSQL. Migration `006_admin_workspace` เพิ่มโครงสร้าง Admin และ `007_service_departments` เพิ่มคิว FAC/FIN/PROC โดยไม่ลบ Ticket หรือบัญชีเดิม. ตอนเริ่ม API จะรัน migration อัตโนมัติ. Demo seed ไม่ทับ priority ของ Ticket ตัวอย่างที่ทีมปรับไว้แล้ว.

UX/UI ใหม่มี Sidebar กรมท่า, ตัวเลขสรุปที่คลิกกรองได้, สีและชื่อเต็มของทั้ง 5 ฝ่าย, แถบขั้นตอน Ticket, เมนูข้อความที่ยังไม่อ่าน, ป้ายงานค้าง, `Ctrl+K`/`Cmd+K` สำหรับค้นหา และธีมสว่าง/มืด (จำเฉพาะธีมใน localStorage ไม่เก็บ token). รองรับจอมือถือและลด animation ตาม `prefers-reduced-motion`.

อัปเดตจากเวอร์ชันเดิม:

```powershell
docker compose up --build -d
docker compose ps
```

เปิด `https://localhost` แล้ว Login ใหม่. ไม่ต้องลบ volume และไม่ต้องสร้าง `.env` ทับของเดิม. รหัสผ่านเดโมเดิมยังใช้งานตามบัญชีที่บันทึกไว้.

API ใหม่: `GET /api/branding` (ชื่อองค์กรสำหรับหน้า Login), `GET /api/settings` (ผู้ใช้ที่ Login), `GET /api/admin/overview`, `GET/POST /api/admin/users`, `PUT /api/admin/users/{id}`, `POST /api/admin/users/{id}/reset-password`, `GET /api/admin/catalog`, `PUT /api/admin/catalog/{IT|HR}`, `PUT /api/admin/settings`, `GET /api/admin/audit` และ `PATCH /api/admin/tickets/{id}/assignee`. ทุกเส้นทาง `/api/admin/*` ตรวจสิทธิ์ Admin ฝั่ง Backend.

## เส้นทางเดโม 5 นาที

1. Login เป็น `employee@example.test`, เลือกหมวด IT อธิบายผลกระทบและสร้าง Ticket.
2. ดูว่าบัตร Ticket แสดงฝ่ายรับผิดชอบ `IT`, สถานะ `Open` และระดับเริ่มต้น `ปกติ`.
3. Logout แล้ว login เป็น `it.agent@example.test`; Ticket อยู่ในคิว IT. Agent ประเมินผลกระทบแล้วปรับระดับเป็นปกติหรือเร่งด่วน โดยมีรายการในไทม์ไลน์ว่าใครเป็นผู้ปรับ.
4. กลับมาเป็น Employee เลือก Ticket แล้วส่งข้อความในส่วน “ข้อความกับเจ้าหน้าที่”.
5. Login เป็น IT Agent แล้วเปิด Ticket เดิม ตอบกลับในแชต และเปลี่ยน `Open → In Progress → Done`.
6. กลับมาเป็น Employee แล้วกดรีเฟรชข้อความ จะเห็นคำตอบของ Operator พร้อมสถานะและไทม์ไลน์ที่อัปเดต.
7. Login เป็น HR Agent เพื่อแสดงว่าไม่เห็น Ticket ฝ่าย IT; Admin เห็นทุกฝ่าย.

API ใช้ bearer token ที่มีอายุ 8 ชั่วโมง. Frontend เก็บ token ในหน่วยความจำของหน้าเว็บ จึงต้อง login ใหม่เมื่อ refresh หน้า. `POST /api/tickets` รับหัวข้อ รายละเอียด ผลกระทบ และหมวดบริการ; Backend กำหนดระดับเริ่มต้นเป็น `Normal` และปฏิเสธค่า priority จากผู้แจ้ง. Agent ที่รับผิดชอบ Ticket และ Admin เปลี่ยนระดับได้ด้วย `PATCH /api/tickets/{id}/priority` พร้อม `{"priority":"Urgent"}` หรือ `Normal`; ระบบบันทึกผู้เปลี่ยนและค่าก่อน/หลังใน `ticket_priority_history` ซึ่งรวมอยู่ในไทม์ไลน์ Ticket. Migration `002_ticket_priority` เพิ่ม priority ให้ Ticket เดิม; `003_ticket_messages` เพิ่มตารางเก็บบทสนทนา; `004_ticket_reads` เก็บตำแหน่งข้อความล่าสุดที่ผู้ใช้แต่ละคนอ่านแล้ว; `005_ticket_triage` เพิ่มข้อมูลผลกระทบและประวัติการปรับระดับ. ใช้ `GET /api/tickets/{id}/messages` เพื่ออ่าน, `POST /api/tickets/{id}/messages` พร้อม `{"body":"ข้อความ"}` เพื่อส่ง (สูงสุด 4,000 ตัวอักษร), `POST /api/tickets/{id}/messages/read` เพื่อทำเครื่องหมายว่าอ่านแล้ว และ `GET /api/unread-counts` เพื่อดูจำนวนข้อความใหม่แยกตาม Ticket. เฉพาะผู้ใช้ที่มีสิทธิ์เห็น Ticket นั้นอ่านและส่งได้. เอกสาร OpenAPI อยู่ที่ `https://localhost/api/docs`.

ตัวอย่างเรียก API (PowerShell):

```powershell
$login = curl.exe -k -s https://localhost/api/login -H 'Content-Type: application/json' -d '{"email":"employee@example.test","password":"YOUR_DEMO_EMPLOYEE_PASSWORD"}' | ConvertFrom-Json
$token = $login.access_token
curl.exe -k -s https://localhost/api/tickets -H "Authorization: Bearer $token"
```

## ทดสอบ

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements-dev.txt
Push-Location backend
..\.venv\Scripts\python -m pytest -q
Pop-Location
```

ทดสอบครอบคลุมการสร้าง Ticket พร้อมผลกระทบ, การเริ่มระดับปกติโดยบังคับ, backend routing, category ที่ไม่ถูกต้อง, การเห็นเฉพาะ Ticket ตาม role, การห้ามข้ามคิว, การอนุญาต Agent/Admin ให้ปรับระดับพร้อมบันทึกประวัติ, การเปลี่ยนสถานะตามลำดับ และการอ่าน/ส่งข้อความพร้อมตรวจสิทธิ์ของบทสนทนา. สำหรับ integration กับ PostgreSQL ให้รัน `docker compose up --build` แล้วทำเส้นทางเดโมข้างต้น.

ตรวจการเปิดพอร์ตบนเครื่อง: `docker compose ps` ต้องแสดง host port เฉพาะ `web` ที่ 80/443. ลอง `curl.exe http://localhost:8000/api/health` และ `Test-NetConnection localhost -Port 5432` จะต้องต่อไม่ได้ (หากไม่มีบริการอื่นบนเครื่องใช้ port เหล่านี้). **Docker Compose บนเครื่องไม่ใช่หลักฐานว่ามี public/private subnet จริง**; network `edge` และ `data` เป็น Docker networks เท่านั้น.

## AWS architecture ตัวอย่าง

```text
Internet :443
    │
    ▼
Public subnets (2 AZ): ALB HTTPS (ACM)
    │ :443 เฉพาะ ALB → Nginx
    ▼
Public subnets: ECS web (React static + Nginx, TLS ภายใน)
    │ /api → :8000 เฉพาะ web SG → API SG
    ▼
Private subnets: ECS FastAPI (assign_public_ip=false)
    │ :5432 เฉพาะ API SG → DB SG
    ▼
Private subnets: RDS PostgreSQL (publicly_accessible=false)
```

Terraform ใช้สอง public subnet และสอง private subnet ในสอง Availability Zones. ALB และ web อยู่ public subnets; API และ RDS อยู่ private subnets. อินเทอร์เน็ตเข้า ALB เฉพาะ 443; web รับจาก ALB เฉพาะ 443; API รับจาก web เฉพาะ 8000; DB รับจาก API เฉพาะ 5432. ไม่มี SSH ingress. Private tasks ออก HTTPS ผ่าน NAT เพื่อดึง image และส่ง logs/อ่าน secrets; NAT **ไม่เปิด inbound** จากอินเทอร์เน็ต. ALB ใช้ ACM certificate สำหรับ hostname จริง; Nginx ใช้ self-signed cert เฉพาะช่วง ALB → web ภายใน VPC. Browser เรียก `/api` ผ่าน ALB และ Nginx ตลอด.

> Terraform เป็นตัวอย่างพร้อมให้ตรวจ/ปรับก่อนใช้จริง ยังไม่มีการ deploy จากโปรเจกต์นี้. AWS ALB, NAT Gateway, ECS, RDS, traffic และ logs มีค่าใช้จ่าย.

### ค่าที่ต้องเตรียมเอง

- AWS account, AWS CLI credentials และ Terraform >= 1.6
- Domain/hostname และ **validated** ACM certificate ใน region เดียวกัน (`certificate_arn`)
- ECR image URI สองตัว (`web_image`, `api_image`); build/push Docker images ก่อน apply
- Secrets Manager secret ที่เก็บ JWT secret เป็น plain string อย่างน้อย 32 ตัวอักษร (`jwt_secret_arn`)
- ถ้าจะเดโมด้วยบัญชีตัวอย่างบน AWS: Secrets Manager secret แบบ plain string สี่ตัวและ `demo_password_secret_arns` ใน `terraform.tfvars` ตาม key ที่ระบุใน `variables.tf`

ตัวอย่างการเตรียม image โดยใช้ ECR repositories ที่คุณสร้างในบัญชีของตน (แทน `ACCOUNT`, `REGION`, `TAG`):

```bash
aws ecr create-repository --repository-name ticketcenter-web --region REGION
aws ecr create-repository --repository-name ticketcenter-api --region REGION
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker build -t ACCOUNT.dkr.ecr.REGION.amazonaws.com/ticketcenter-web:TAG ./frontend
docker build -t ACCOUNT.dkr.ecr.REGION.amazonaws.com/ticketcenter-api:TAG ./backend
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/ticketcenter-web:TAG
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/ticketcenter-api:TAG
```

จากนั้น:

```bash
cd infra/aws
cp terraform.tfvars.example terraform.tfvars
# ใส่ ARN/URI จริงใน terraform.tfvars; ห้าม commit ไฟล์นี้
terraform init
terraform fmt -check
terraform validate
terraform plan
# terraform apply เฉพาะเมื่อคุณตรวจ plan และยอมรับค่าใช้จ่ายแล้ว
```

ตั้ง DNS CNAME/alias ของ hostname ให้ชี้ไปที่ `alb_dns_name` ที่ Terraform output แสดง. ใบรับรองต้องครอบคลุม hostname นี้. ตัวอย่างนี้ไม่สร้าง DNS record ให้ เพราะผู้ใช้อาจใช้ผู้ให้บริการ DNS คนละราย. `terraform.tfvars` เก็บเพียง ARN/URI ไม่ต้องใส่ secret value; RDS สร้างและจัดการรหัสผ่านผ่าน Secrets Manager แล้ว ECS inject เป็น environment variable. อย่า commit state หรือไฟล์ secret. เก็บ Terraform state ใน backend ที่เข้ารหัสและจำกัดสิทธิ์เมื่อใช้ร่วมกัน.

### ตรวจข้อกำหนดเครือข่ายหลัง deploy

1. `terraform output api_subnet_ids` ต้องตรงกับ private subnet ใน ECS API service; `assign_public_ip` ต้องเป็น `DISABLED`.
2. `terraform output db_publicly_accessible` ต้องเป็น `false`; RDS อยู่ DB subnet group ของ private subnets.
3. ตรวจ Security Group: ALB ingress 443 จาก internet, web ingress 443 จาก ALB SG, API ingress 8000 จาก web SG, DB ingress 5432 จาก API SG; ไม่มีกฎ SSH.
4. จากเครื่องภายนอกลองเชื่อมต่อโดยตรงไป port 8000/5432 ของ ALB hostname: ต้องไม่สำเร็จ. API/RDS ไม่มี public address ให้ยิงตรง; แสดงหลักฐานจาก ECS/RDS console ประกอบ. ทดสอบเว็บผ่าน hostname จริงโดยไม่มี `-k`.

## ข้อจำกัด MVP

- บัญชีเดโมเริ่มต้นถูก seed จาก environment variables; Admin จัดการบัญชีและรีเซ็ตรหัสผ่านได้แล้ว. ยังไม่มี self-service password reset หรือ SSO.
- Dashboard นับเฉพาะ Ticket ที่ role นั้นมองเห็น (Admin เห็นทั้งระบบ).
- ยังไม่มี attachment, push notification หรือ pagination; มีตัวเลขข้อความที่ยังไม่อ่านและเมนูข้อความบนเว็บผ่าน event stream แบบทันทีแล้ว.
- ตัวอย่าง AWS ใช้ NAT Gateway เดียวเพื่อลดค่าใช้จ่าย จึงไม่มี high availability ของทางออกอินเทอร์เน็ตข้าม AZ.

## UX/UI รอบ Impeccable (8 ตุลาคม 2026)

- หน้า Login และทุกบทบาทใช้ชุดสีเดียวกัน: Sidebar กรมท่า ปุ่มน้ำเงิน พื้นทำงานสว่างและแชทเทาอ่อน พร้อมธีมมืด
- ใช้ **Noto Sans Thai** ที่เก็บไฟล์และใบอนุญาตใน `frontend/public/fonts` ไม่ต้องโหลดฟอนต์จากเว็บภายนอกขณะใช้งาน
- บนคอม รายการ Ticket และรายละเอียดเลื่อนแยกกัน; บนมือถือกด Ticket เพื่อเปิดรายละเอียดแล้วใช้ “กลับไปรายการคำขอ”
- รายละเอียดและผลกระทบกดขยายได้ แชทของบัญชีปัจจุบันอยู่ขวา ข้อความอีกฝ่ายอยู่ซ้าย พร้อมชื่อและเวลา
- Admin เริ่มที่งานเร่งด่วน งานยังไม่มอบหมายและงานค้าง กดตัวเลขเพื่อเข้าคิวที่กรองไว้ได้
- หน้าผู้ใช้ หมวดบริการ ตั้งค่าระบบ และประวัติผู้ดูแลใช้ฟอร์ม/ตารางแบบเดียวกัน และมีหน้าต่างยืนยันก่อนบันทึก
- การปรับความเร่งด่วน อัปเดตสถานะ มอบหมายงาน และออกจากระบบมีการยืนยัน; หน้าต่างรองรับ Tab และ Escape
- ตัวเลขข้อความที่ยังไม่อ่านอัปเดตผ่าน event stream; บนมือถือไม่ทำเครื่องหมายอ่านจนกว่าจะเปิดรายละเอียด

อัปเดตเฉพาะ Frontend บนเครื่อง:

```powershell
docker compose build web
docker compose up -d --no-deps web
```

เปิด `https://localhost` แล้วกด **Ctrl+F5**. ข้อมูลเดิมใน PostgreSQL ยังคงอยู่.

### ทดสอบ UI ด้วยเบราว์เซอร์อัตโนมัติ

ใช้บัญชีเดโมจาก `.env` และต้องเปิด Docker Compose ก่อน ชุดตรวจนี้อ่านข้อมูล เปิด/ยกเลิกแบบฟอร์ม และตรวจ role navigation, search, ธีม, การยืนยัน, ฟอนต์ และมือถือ โดยไม่สร้าง Ticket/แก้บัญชีหรือการตั้งค่า; การอ่านบทสนทนาอาจเปลี่ยน read receipt ตามการใช้งานปกติ.

```powershell
python -m pip install -r frontend/tests/requirements.txt
python -m playwright install chromium
python frontend/tests/ui_smoke.py
```

รูปและผลการตรวจอยู่ใน `.test-artifacts/ui-smoke` (ไม่ commit). คู่มือชุดสี ขนาดตัวอักษรและ component อยู่ใน `DESIGN.md`; ข้อมูลธุรกิจและข้อจำกัดอยู่ใน `PRODUCT.md`.


## ฝ่ายบริการเพิ่มและแชทแบบทันที

| รหัสคิว | ฝ่าย | ตัวอย่างคำขอ |
|---|---|---|
| IT | เทคโนโลยีสารสนเทศ | อุปกรณ์ เครือข่าย ระบบงาน |
| HR | ทรัพยากรบุคคล | วันลา สวัสดิการ ข้อมูลพนักงาน |
| FAC | อาคารและสถานที่ / ธุรการ | แอร์ ไฟ ห้องประชุม โต๊ะ/เก้าอี้ |
| FIN | การเงินและบัญชี | เบิกค่าใช้จ่าย เอกสารภาษี การชำระเงิน |
| PROC | จัดซื้อ | อุปกรณ์สำนักงาน คำขอซื้อ ข้อมูลผู้ขาย |

Admin เห็นคิวทั้ง 5 ฝ่าย; Agent เห็นเฉพาะฝ่ายตน. สร้าง Agent ใหม่ที่ **ผู้ใช้และสิทธิ์ → เพิ่มผู้ใช้ → เจ้าหน้าที่ → เลือกฝ่าย**. การสร้าง Ticket ยังคงเริ่ม Normal และ Backend ตรวจหมวด/การเปิดรับงานก่อนกำหนดคิว; ผู้เรียก API เปลี่ยนคิวด้วย field `department` เองไม่ได้.

เมื่อเปิด `DEMO_SEED=true` จะมี Ticket ตัวอย่างของทั้ง 5 ฝ่าย. Agent เดโมสามฝ่ายใหม่เป็นตัวเลือก: ใส่รหัสผ่านที่คุณกำหนดเองใน `.env` ที่ `DEMO_FAC_PASSWORD`, `DEMO_FIN_PASSWORD`, `DEMO_PROC_PASSWORD` แล้วรัน Compose ใหม่เพื่อ seed บัญชี `fac.agent@example.test`, `fin.agent@example.test`, `proc.agent@example.test`. เว้นว่างเพื่อข้ามการสร้างบัญชีเหล่านี้และใช้หน้า Admin สร้างบัญชีจริงแทน. บัญชีที่มีอยู่แล้วไม่ถูก seed ทับรหัสผ่าน.

### การทำงานของข้อความ

1. ส่งข้อความด้วย REST `POST /api/tickets/{id}/messages` และบันทึกใน PostgreSQL.
2. ใน transaction เดียวกัน API ส่ง metadata ผ่าน PostgreSQL `NOTIFY`; เหตุการณ์ถูกส่งหลัง commit.
3. Browser เปิด **SSE** ที่ `GET /api/events` ผ่าน Nginx/HTTPS โดยใส่ JWT ใน Authorization header. ไม่มี token ใน URL.
4. เซิร์ฟเวอร์ส่งเฉพาะเหตุการณ์ของ Ticket ที่บัญชีนั้นมีสิทธิ์; Frontend โหลดเนื้อหาผ่าน REST ที่ตรวจสิทธิ์อีกครั้ง. ข้อความของตนอยู่ขวา อีกฝ่ายอยู่ซ้าย และข้อความซ้ำถูกตัดด้วย message ID.
5. ถ้าเปิด Ticket อื่นจะขึ้นจำนวนข้อความที่ยังไม่อ่านในรายการนั้น; เมื่อเปิดบทสนทนาจะทำเครื่องหมายอ่าน. การเปลี่ยนสถานะและ Ticket ใหม่เข้าคิวผ่าน stream เช่นกัน.
6. เมื่อการเชื่อมต่อขาด Browser ลองต่อใหม่ และโหลด snapshot ปัจจุบันเมื่อเชื่อมต่อกลับ เพื่อเก็บข้อความที่เกิดระหว่างหลุด. แสดงสถานะการเชื่อมต่อในหัวข้อบทสนทนา.

Nginx ปิด buffering/cache เฉพาะ `/api/events`, ใช้ HTTP/1.1 ไป API และมี heartbeat ป้องกัน idle timeout. ใช้เส้นทางและพอร์ตเดิม จึงยังเปิดออกอินเทอร์เน็ตเพียง 443/80 ของเว็บ. แต่ละแท็บใช้หนึ่ง PostgreSQL listening connection; เหมาะกับ MVP และต้องวางแผน connection limit เมื่อขยายจำนวนผู้ใช้. SQLite รองรับ REST unit tests; endpoint realtime ต้องใช้ PostgreSQL. Browser notification ของระบบปฏิบัติการและ attachment ยังเป็นงานพัฒนาต่อ.

พื้นที่อ่านข้อความบน Desktop สูงอย่างน้อย 320 พิกเซล ให้เห็นประมาณ 3 ข้อความสั้น ๆ รายละเอียด/ผู้รับผิดชอบและประวัติกดเปิดได้โดยไม่บีบแชทหรือทับช่องส่ง บนจอเตี้ยเลื่อนส่วนรายละเอียดเพื่อไปยังช่องส่งและกิจกรรมได้ ปุ่ม **ขยายพื้นที่ทำงาน** ที่แถบบนซ่อน Sidebar/ตัวเลขสรุปเพื่อเพิ่มพื้นที่ แล้วกด **คืนมุมมองปกติ** เพื่อกลับ. ข้อมูล/สิทธิ์ไม่เปลี่ยนตามการขยายหน้า.

### ตรวจสองหน้าต่างและการเชื่อมต่อกลับ

```powershell
python frontend/tests/realtime_smoke.py
```

ชุดตรวจเปิดหน้าต่างแยกใน browser context เดียวด้วย Employee และ IT Agent ส่งข้อความไปกลับโดยไม่ reload, ตรวจ unread badge เมื่อ Agent เปิดงานอื่น, ตรวจการเปลี่ยนสถานะทันทีและต่อกลับหลังจำลอง offline. ตรวจหมวด/ตัวเลือกฝ่ายครบ 5 ฝ่าย และลบเฉพาะ Ticket ทดสอบที่สร้างด้วยรหัสเฉพาะของการตรวจครั้งนั้น. รูป ผลเวลาและผลตรวจอยู่ใน `.test-artifacts/realtime`. ต้องรันจากเครื่องที่เข้าถึง Docker Compose ของโปรเจกต์นี้ได้.
