"""Two windows, separate accounts: real HTTPS chat, unread badges and reconnect.

Requires local Docker Compose and DEMO_* credentials in .env. Only tickets
created by this run are cleaned up; existing organization records are untouched.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import subprocess
import time
import uuid
import sys
import traceback

# Playwright's accessibility snapshots can include a filled password field.
sys.excepthook=lambda kind,error,trace: print(''.join(traceback.format_tb(trace))+kind.__name__+': '+str(error).split('Aria snapshot:')[0],file=sys.stderr)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.test-artifacts/realtime';OUT.mkdir(parents=True,exist_ok=True)
env={}
for line in (ROOT/'.env').read_text(encoding='utf-8-sig').splitlines():
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1);env[k]=v.strip().strip('"').strip("'")
prefix='UI realtime '+uuid.uuid4().hex[:10]
created=[]; errors=[]; latency={}; dimensions={}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(ignore_https_errors=True,base_url='https://localhost',viewport={'width':1440,'height':1000},reduced_motion='reduce')
        for attempt in range(60):
            if context.request.get('/api/health').status==200:break
            time.sleep(.25)
        else:raise RuntimeError('Local API is not ready; start Docker Compose first.')
        employee=context.new_page();operator=context.new_page();admin=context.new_page()
        for page in (employee,operator,admin):page.on('pageerror',lambda e:errors.append(str(e)))
        def login(page,email,key,heading):
            page.goto('/');page.get_by_label('อีเมล',exact=True).fill(email);page.get_by_label('รหัสผ่าน',exact=True).fill(env[key]);page.get_by_role('button',name='เข้าสู่ระบบ',exact=True).click()
            expect(page.get_by_role('heading',name=heading,exact=True)).to_be_visible()
            if heading!='ภาพรวมองค์กร':expect(page.locator('.list-footer')).not_to_contain_text('อัปเดต …')
        def snap(page,name):
            page.evaluate('document.fonts.ready');page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            page.screenshot(path=str(OUT/(name+'.png')),full_page=True,animations='disabled')
        login(employee,'employee@example.test','DEMO_EMPLOYEE_PASSWORD','คำขอของฉัน')
        login(operator,'it.agent@example.test','DEMO_IT_PASSWORD','คิวบริการ · ฝ่ายเทคโนโลยีสารสนเทศ (IT)')
        login(admin,'admin@example.test','DEMO_ADMIN_PASSWORD','ภาพรวมองค์กร')
        expect(operator.locator('.chat-connection')).to_contain_text('เชื่อมต่อแล้ว',timeout=8000)
        credentials=context.request.post('/api/login',data={'email':'employee@example.test','password':env['DEMO_EMPLOYEE_PASSWORD']}).json()
        headers={'Authorization':'Bearer '+credentials['access_token']}
        def create(category,suffix):
            employee.get_by_role('button',name='แจ้งคำขอใหม่',exact=True).click()
            employee.get_by_label('หมวดบริการ',exact=False).select_option(category)
            employee.get_by_label('หัวข้อ',exact=True).fill(prefix+' '+suffix)
            employee.get_by_label('ผลกระทบที่เกิดขึ้น',exact=True).fill('ทดสอบระบบ ไม่ใช่คำขอจริงขององค์กร')
            employee.get_by_label('รายละเอียด',exact=True).fill('คำขอตัวอย่างสำหรับตรวจการส่งข้อความและคิวบริการ')
            with employee.expect_response(lambda r:r.url.endswith('/api/tickets') and r.request.method=='POST') as saved:
                employee.get_by_role('button',name='ส่งคำขอ',exact=True).click()
            ticket=saved.value.json();assert saved.value.status==201;created.append(ticket['id'])
            expect(employee.locator('.detail-header h2')).to_have_text(prefix+' '+suffix)
            expect(employee.locator('.chat-connection')).to_contain_text('เชื่อมต่อแล้ว')
            return ticket
        ticket=create('IT','conversation')
        row=operator.locator('.ticket-row').filter(has_text=prefix+' conversation')
        expect(row).to_be_visible(timeout=3000);row.click()
        expect(operator.locator('.detail-header h2')).to_have_text(prefix+' conversation')
        def send(sender,receiver,text):
            start=time.perf_counter()
            sender.get_by_label('ข้อความในคำขอ',exact=True).fill(text);sender.get_by_label('ข้อความในคำขอ',exact=True).press('Enter')
            expect(receiver.locator('.chat-message.theirs').filter(has_text=text)).to_be_visible(timeout=3000)
            expect(sender.locator('.chat-message.mine').filter(has_text=text)).to_have_count(1)
            expect(receiver.locator('.chat-message.theirs').filter(has_text=text)).to_have_count(1)
            return round(time.perf_counter()-start,3)
        latency['employee_to_operator']=send(employee,operator,'พนักงาน: ส่งถึงทีมทันทีโดยไม่ต้องรีเฟรช')
        latency['operator_to_employee']=send(operator,employee,'เจ้าหน้าที่: รับข้อความแล้วครับ กำลังตรวจสอบ')
        latency['third_message']=send(employee,operator,'ขอบคุณครับ รอผลการตรวจสอบ')
        snap(employee,'employee-live');snap(operator,'operator-live')
        dimensions['default_feed_height']=operator.locator('.conversation-feed').evaluate('(e)=>Math.round(e.getBoundingClientRect().height)')
        assert dimensions['default_feed_height']>=320,dimensions
        default_width=operator.locator('.detail-pane').bounding_box()['width']
        operator.get_by_role('button',name='ขยายพื้นที่ทำงาน',exact=True).click()
        dimensions['expanded_feed_height']=operator.locator('.conversation-feed').evaluate('(e)=>Math.round(e.getBoundingClientRect().height)')
        assert dimensions['expanded_feed_height']>=dimensions['default_feed_height'],dimensions
        assert operator.locator('.detail-pane').bounding_box()['width']>default_width+80
        snap(operator,'expanded-chat')
        operator.get_by_role('button',name='คืนมุมมองปกติ',exact=True).click()
        # Expanded activity/details must not compress or overlap chat controls,
        # including a short desktop and a narrow mobile detail view.
        for width,height in ((1280,720),(1440,1000),(390,844)):
            operator.set_viewport_size({'width':width,'height':height})
            if width<=900 and not operator.locator('.detail-pane').is_visible():row.click()
            for details_open,history_open,label in ((False,False,'closed'),(True,False,'details'),(False,True,'history'),(True,True,'both')):
                for selector,wanted in (('.request-details',details_open),('.timeline-section',history_open)):
                    section=operator.locator(selector)
                    if bool(section.get_attribute('open') is not None)!=wanted:section.locator('summary').click()
                feed=operator.locator('.conversation-feed')
                assert feed.bounding_box()['height']>=320
                expect(feed.locator('.chat-message')).to_have_count(3)
                bubbles=feed.locator('.chat-message').all()
                assert len(bubbles)==3
                assert all(b.bounding_box()['y']>=feed.bounding_box()['y'] and b.bounding_box()['y']+b.bounding_box()['height']<=feed.bounding_box()['y']+feed.bounding_box()['height'] for b in bubbles),'Three short messages do not fit'
                feed.scroll_into_view_if_needed()
                if width>900:
                    body=operator.locator('.detail-body').bounding_box()
                    assert feed.bounding_box()['y']>=body['y']-1 and feed.bounding_box()['y']+feed.bounding_box()['height']<=body['y']+body['height']+1,'Feed cannot be fully viewed: '+str((width,label,body,feed.bounding_box()))
                snap(operator,f'layout-{width}-{label}-three-messages')
                composer=operator.locator('.chat-composer');history=operator.locator('.timeline-section')
                assert history.bounding_box()['y']>=composer.bounding_box()['y']+composer.bounding_box()['height'],'Activity overlaps composer'
                send_button=composer.locator('button');send_button.scroll_into_view_if_needed()
                assert 0<=send_button.bounding_box()['y'] and send_button.bounding_box()['y']+send_button.bounding_box()['height']<=height,'Send button unreachable'
                snap(operator,f'layout-{width}-{label}-composer')
                if history_open:
                    history.scroll_into_view_if_needed();snap(operator,f'layout-{width}-{label}-activity')
                assert operator.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Horizontal page overflow'
            for selector in ('.request-details','.timeline-section'):
                section=operator.locator(selector)
                if section.get_attribute('open') is not None:section.locator('summary').click()
        operator.set_viewport_size({'width':1440,'height':1000})
        # An unread notification belongs to a ticket that is not currently open.
        alternate=create('IT','other window')
        expect(operator.locator('.ticket-row').filter(has_text=prefix+' other window')).to_be_visible(timeout=3000)
        operator.locator('.ticket-row').filter(has_text=prefix+' other window').click()
        employee.locator('.ticket-row').filter(has_text=prefix+' conversation').click()
        employee.get_by_label('ข้อความในคำขอ',exact=True).fill('ข้อความใหม่ขณะเจ้าหน้าที่เปิดงานอื่น')
        employee.get_by_label('ข้อความในคำขอ',exact=True).press('Enter')
        unread=row.locator('.unread-badge');expect(unread).to_contain_text('1',timeout=3000);snap(operator,'unread-notification')
        row.click();expect(operator.locator('.chat-message.theirs').filter(has_text='ข้อความใหม่ขณะเจ้าหน้าที่เปิดงานอื่น')).to_be_visible(timeout=3000)
        expect(row.locator('.unread-badge')).to_have_count(0,timeout=3000)
        # A real status transition reaches the other account through the same stream.
        operator.get_by_role('button',name='รับงาน · เริ่มดำเนินการ',exact=True).click();operator.get_by_role('button',name='ยืนยันรับงาน',exact=True).click()
        expect(employee.locator('.detail-badges .mini-status')).to_contain_text('กำลังดำเนินการ',timeout=3000)
        employee.locator('.timeline-section summary').click();expect(employee.locator('.timeline li')).to_have_count(2);employee.locator('.timeline-section summary').click()
        # Offline affects this test browser only. No server or user browser restarts.
        context.set_offline(True)
        expect(operator.locator('.chat-connection')).to_contain_text('กำลังเชื่อมต่อ',timeout=7000)
        context.set_offline(False)
        expect(operator.locator('.chat-connection')).to_contain_text('เชื่อมต่อแล้ว',timeout=15000)
        expect(employee.locator('.chat-connection')).to_contain_text('เชื่อมต่อแล้ว',timeout=15000)
        latency['after_reconnect']=send(employee,operator,'เชื่อมต่อกลับแล้ว ข้อความยังส่งได้ทันที')
        for code in ('FAC','FIN','PROC'):
            result=create(code,code+' request');assert result['department']==code
        expect(admin.locator('.department-card')).to_have_count(5)
        snap(admin,'five-departments')
        admin.get_by_role('button',name='ผู้ใช้และสิทธิ์',exact=True).click();admin.get_by_role('button',name='เพิ่มผู้ใช้',exact=True).click()
        admin.get_by_role('dialog').get_by_label('บทบาท',exact=False).select_option('agent')
        options=admin.get_by_role('dialog').get_by_label('ฝ่าย',exact=False).locator('option')
        expect(options).to_have_count(5)
        snap(admin,'five-department-assignment');admin.get_by_role('button',name='ยกเลิก',exact=True).click()
        # Endpoint authorization remains enforced; query-string tokens aren't accepted.
        assert context.request.get('/api/events').status==401
        assert context.request.get('/api/events?token=invalid').status==401
        hr=context.request.post('/api/login',data={'email':'hr.agent@example.test','password':env['DEMO_HR_PASSWORD']}).json()
        assert context.request.get(f"/api/tickets/{ticket['id']}/messages",headers={'Authorization':'Bearer '+hr['access_token']}).status==404
        assert not errors,errors
        context.close();browser.close()
finally:
    if created:
        # Delete only this run's exact IDs and prefix, through SQL parameters.
        code="""import json,sys
from sqlalchemy import create_engine,text
import os,urllib.parse
url='postgresql+psycopg://%s:%s@%s:5432/%s'%(os.environ['DB_USER'],urllib.parse.quote(os.environ['DB_PASSWORD'],safe=''),os.environ['DB_HOST'],os.environ['DB_NAME'])
with create_engine(url).begin() as c:
 for ticket_id in json.loads(sys.argv[1]):
  row=c.execute(text('SELECT title FROM tickets WHERE id=:id'),{'id':ticket_id}).scalar()
  if row is not None:
   assert row.startswith(sys.argv[2]),'Refusing to remove a non-test ticket'
   c.execute(text('DELETE FROM tickets WHERE id=:id'),{'id':ticket_id})
 c.execute(text('SELECT pg_notify(:channel,:payload)'),{'channel':'ticketcenter_events','payload':'{\"type\":\"workspace.updated\"}'})
"""
        result=subprocess.run(['docker','compose','exec','-T','api','python','-c',code,json.dumps(created),prefix],cwd=ROOT,capture_output=True,text=True)
        assert result.returncode==0,'Failed to clean this run\'s test tickets; inspect Docker logs.'
report={'status':'pass','delivery_seconds':latency,'chat_height_px':dimensions,'javascript_errors':errors,'checks':['two accounts in separate windows','bidirectional immediate delivery','three short messages fit at 1280/1440/390px','expanded details/activity never overlap composer','composer reachable in all four expansion states','no duplicate messages','per-ticket unread badge','live status update','reconnection','five service queues','five agent department options','authorization preserved'],'test_tickets_cleaned':len(created)}
(OUT/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
