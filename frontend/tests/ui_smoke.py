from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import sys

sys.excepthook=lambda kind,error,trace: print(kind.__name__+': '+str(error).split('Aria snapshot:')[0],file=sys.stderr)

root=Path(__file__).resolve().parents[2]; out=root/'.test-artifacts/ui-smoke'; out.mkdir(parents=True,exist_ok=True)
env={}
for line in (root/'.env').read_text(encoding='utf-8-sig').splitlines():
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1);env[k]=v.strip().strip('"').strip("'")
errors=[]; checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    context=browser.new_context(ignore_https_errors=True,viewport={'width':1440,'height':1000},base_url='https://localhost',reduced_motion='reduce')
    page=context.new_page(); page.on('pageerror',lambda e:errors.append(str(e)))
    def capture(name):
        expect(page.locator('.admin-loading')).to_have_count(0)
        page.evaluate('document.fonts.ready')
        page.evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        page.evaluate('window.scrollTo(0,0)')
        page.screenshot(path=str(out/(name+'.png')),full_page=True,animations='disabled')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),name+' document overflow'
        checks.append(name)
    def login(email,key,heading):
        page.goto('/')
        page.get_by_label('อีเมล',exact=True).fill(email)
        page.get_by_label('รหัสผ่าน',exact=True).fill(env[key])
        page.get_by_role('button',name='เข้าสู่ระบบ',exact=True).click()
        expect(page.get_by_role('heading',name=heading,exact=True)).to_be_visible()
        if heading != 'ภาพรวมองค์กร':
            expect(page.locator('.list-footer')).not_to_contain_text('อัปเดต …')
        else:
            expect(page.locator('.admin-loading')).to_have_count(0)
            expected=page.locator('.metric strong').first.text_content()
            expect(page.locator('.sidebar .inbox-nav > b')).to_have_text(expected)
    def theme(dark):
        actual=page.locator('html').get_attribute('data-theme')
        if (actual=='dark') != dark:
            page.get_by_role('button',name='เปลี่ยนเป็นธีม'+('มืด' if dark else 'สว่าง'),exact=True).click()
    page.goto('/'); capture('login')
    page.set_viewport_size({'width':390,'height':844}); capture('mobile-login'); page.set_viewport_size({'width':1440,'height':1000})
    assert context.request.get('/fonts/noto-sans-thai-0.ttf').headers.get('content-type','').startswith(('font/','application/')), 'Font not served'
    login('admin@example.test','DEMO_ADMIN_PASSWORD','ภาพรวมองค์กร'); theme(False); capture('desktop')
    theme(True); capture('dark'); theme(False)
    for name,shot in [('ผู้ใช้และสิทธิ์','users'),('หมวดบริการ','catalog'),('ตั้งค่าระบบ','settings'),('ประวัติผู้ดูแล','audit')]:
        page.get_by_role('button',name=name,exact=True).click()
        expect(page.get_by_role('heading',name=name,exact=True)).to_be_visible(); capture(shot)
    page.get_by_role('button',name='ผู้ใช้และสิทธิ์',exact=True).click()
    page.get_by_role('button',name='เพิ่มผู้ใช้',exact=True).click(); expect(page.get_by_role('dialog')).to_be_visible(); capture('user-dialog')
    page.keyboard.press('Escape'); expect(page.get_by_role('dialog')).to_have_count(0)
    page.get_by_role('button',name='ภาพรวมองค์กร',exact=True).click()
    page.get_by_role('button',name='ยังไม่มีผู้รับผิดชอบ',exact=False).click()
    expect(page.locator('.focus-filter')).to_contain_text('ยังไม่มอบหมาย')
    expect(page.locator('.chat-empty').filter(has_text='กำลังโหลดข้อความ')).to_have_count(0)
    capture('admin-inbox')
    page.keyboard.press('Control+k'); expect(page.get_by_label('ค้นหา Ticket',exact=True)).to_be_focused()
    page.get_by_label('ค้นหา Ticket',exact=True).fill('no-matching-ticket-abc123'); expect(page.get_by_role('heading',name='ไม่พบ Ticket',exact=True)).to_be_visible(); capture('empty-filter')
    page.get_by_role('button',name='ภาพรวมองค์กร',exact=True).click(); page.set_viewport_size({'width':390,'height':844}); capture('mobile')
    page.get_by_role('button',name='ตั้งค่าระบบ',exact=True).click(); capture('mobile-settings')
    page.set_viewport_size({'width':1440,'height':1000})
    login('employee@example.test','DEMO_EMPLOYEE_PASSWORD','คำขอของฉัน')
    expect(page.get_by_role('button',name='ตั้งค่าระบบ',exact=True)).to_have_count(0)
    expect(page.locator('.chat-empty').filter(has_text='กำลังโหลดข้อความ')).to_have_count(0); capture('employee')
    for width,height in [(1280,720),(800,1000),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height}); capture('user-'+str(width))
        if width>900:
            page.locator('.chat-composer button').scroll_into_view_if_needed()
            bounds=page.locator('.chat-composer button').evaluate('(e)=>({bottom:e.getBoundingClientRect().bottom,height:e.getBoundingClientRect().height})')
            assert bounds['bottom']<=height and bounds['height']>20,'Chat send button clipped at '+str(width)
    page.set_viewport_size({'width':1440,'height':1000})
    page.get_by_role('button',name='แจ้งคำขอใหม่',exact=True).click(); expect(page.get_by_role('dialog')).to_be_visible(); capture('composer')
    page.get_by_label('หัวข้อ',exact=True).fill('ทดสอบแบบฟอร์ม')
    page.keyboard.press('Escape'); expect(page.get_by_role('dialog')).to_have_count(0)
    page.get_by_role('button',name='ออกจากระบบ',exact=True).click(); expect(page.get_by_role('alertdialog')).to_be_visible(); capture('logout-confirm')
    page.get_by_role('button',name='ยกเลิก',exact=True).click(); expect(page.get_by_role('heading',name='คำขอของฉัน')).to_be_visible()
    page.set_viewport_size({'width':390,'height':844}); capture('mobile-inbox')
    expect(page.locator('.detail-pane')).not_to_be_visible()
    page.locator('.ticket-row').first.click(); expect(page.locator('.detail-pane')).to_be_visible()
    expect(page.locator('.chat-empty').filter(has_text='กำลังโหลดข้อความ')).to_have_count(0); capture('mobile-detail')
    page.get_by_role('button',name='กลับไปรายการคำขอ',exact=True).click(); expect(page.locator('.ticket-list')).to_be_visible()
    page.set_viewport_size({'width':1440,'height':1000})
    login('it.agent@example.test','DEMO_IT_PASSWORD','คิวบริการ · ฝ่ายเทคโนโลยีสารสนเทศ (IT)')
    expect(page.locator('.sidebar')).not_to_contain_text('ฝ่ายทรัพยากรบุคคล')
    expect(page.locator('.chat-empty').filter(has_text='กำลังโหลดข้อความ')).to_have_count(0); capture('it-agent')
    priority=page.get_by_label('กำหนดระดับความเร่งด่วน',exact=True)
    if priority.count():
        before=priority.input_value(); priority.select_option('Normal' if before=='Urgent' else 'Urgent')
        expect(page.get_by_role('alertdialog')).to_contain_text('ยืนยันปรับความเร่งด่วน'); capture('priority-confirm')
        page.get_by_role('button',name='ยกเลิก',exact=True).click(); expect(priority).to_have_value(before)
    start=page.get_by_role('button',name='รับงาน · เริ่มดำเนินการ',exact=True)
    if start.count():
        start.click(); expect(page.get_by_role('alertdialog')).to_be_visible(); page.get_by_role('button',name='ยกเลิก',exact=True).click()
    theme(True); capture('dark-inbox')
    for width,height in ((1280,720),(1440,1000)):
        page.set_viewport_size({'width':width,'height':height})
        for selector in ('.request-details','.timeline-section'):
            section=page.locator(selector)
            if section.get_attribute('open') is None:section.locator('summary').click()
        composer=page.locator('.chat-composer');history=page.locator('.timeline-section')
        assert page.locator('.conversation-feed').bounding_box()['height']>=320
        assert history.bounding_box()['y']>=composer.bounding_box()['y']+composer.bounding_box()['height'],'Dark activity overlaps composer'
        composer.locator('button').scroll_into_view_if_needed();capture('dark-'+str(width)+'-both-composer')
        history.scroll_into_view_if_needed();capture('dark-'+str(width)+'-both-activity')
    for selector in ('.request-details','.timeline-section'):
        section=page.locator(selector)
        if section.get_attribute('open') is not None:section.locator('summary').click()
    theme(False)
    login('hr.agent@example.test','DEMO_HR_PASSWORD','คิวบริการ · ฝ่ายทรัพยากรบุคคล (HR)')
    expect(page.locator('.sidebar')).not_to_contain_text('ฝ่ายเทคโนโลยีสารสนเทศ')
    expect(page.locator('.chat-empty').filter(has_text='กำลังโหลดข้อความ')).to_have_count(0); capture('hr-agent')
    assert not errors,errors
    browser.close()
(out/'checks.json').write_text(json.dumps({'screens':checks,'javascript_errors':errors,'checks':'all passed','mutations':'no tickets/settings/accounts changed; normal chat read receipts only'},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: '+str(len(checks))+' views; role navigation, filters, modals, mobile list/detail, fonts and no JavaScript errors.')
