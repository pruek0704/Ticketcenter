import React, { useEffect, useRef, useState } from 'react';
import { Icon } from './icons';
import { DEPARTMENT_FULL, DEPARTMENT_CODES } from './departments';

export const ADMIN_PAGES = [
  ['overview', 'ภาพรวมองค์กร', 'grid'], ['users', 'ผู้ใช้และสิทธิ์', 'users'],
  ['catalog', 'หมวดบริการ', 'catalog'], ['settings', 'ตั้งค่าระบบ', 'settings'], ['audit', 'ประวัติผู้ดูแล', 'history'],
];
const ROLE = { employee: 'พนักงาน', agent: 'เจ้าหน้าที่', admin: 'ผู้ดูแลระบบ' };
const ACTION = { 'settings.updated': 'ปรับตั้งค่าระบบ', 'user.created': 'สร้างผู้ใช้', 'user.updated': 'แก้ไขสิทธิ์หรือบัญชี', 'user.password_reset': 'รีเซ็ตรหัสผ่าน', 'catalog.updated': 'ปรับหมวดบริการ', 'ticket.assigned': 'มอบหมายผู้รับผิดชอบ' };
const time = value => new Date(value).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' });

export function Dialog({ title, children, onClose, busy = false, small = false }) {
  const ref = useRef(null);
  useEffect(() => {
    const previous = document.activeElement;
    const box = ref.current;
    box?.querySelector('input,button,select,textarea')?.focus();
    function keyboard(event) {
      if (event.key === 'Escape' && !busy) { event.preventDefault(); onClose(); }
      if (event.key !== 'Tab') return;
      const items = [...box.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled)')];
      const first = items[0], last = items.at(-1);
      if (!items.length) { event.preventDefault(); return; }
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    box?.addEventListener('keydown', keyboard);
    return () => { box?.removeEventListener('keydown', keyboard); previous?.focus(); };
  }, [busy]);
  return <div className="modal-backdrop admin-modal-backdrop" onMouseDown={event => event.target === event.currentTarget && !busy && onClose()}><section ref={ref} className={`admin-modal ${small ? 'small' : ''}`} role="dialog" aria-modal="true" aria-labelledby="admin-modal-title"><div className="admin-modal-heading"><h2 id="admin-modal-title">{title}</h2><button type="button" className="close-button" onClick={onClose} disabled={busy} aria-label="ปิดหน้าต่าง"><Icon name="close" size={18}/></button></div>{children}</section></div>;
}

export default function AdminWorkspace({ page, revision, request, currentUser, onSettingsChanged, onOpenQueue, onUsersChanged }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [pending, setPending] = useState(null);
  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  async function load() {
    const [overview, users, catalog, settings, audit] = await Promise.all(['/admin/overview', '/admin/users', '/admin/catalog', '/settings', '/admin/audit'].map(path => request(path)));
    setData({ overview, users, catalog, settings, audit });
    onUsersChanged(users);
  }
  useEffect(() => { let live = true; setLoading(true); load().catch(err => { if (live) setError(err.message); }).finally(() => { if (live) setLoading(false); }); return () => { live = false; }; }, []);
  useEffect(() => { setError(''); setSuccess(''); setQuery(''); }, [page]);
  async function perform(action) {
    setBusy(true); setError('');
    try {
      await action.run(); await load(); await onSettingsChanged(); setEditing(null); setPending(null); setSuccess(action.success || 'บันทึกการเปลี่ยนแปลงแล้ว');
    } catch (err) { setError(err.message); setPending(null); } finally { setBusy(false); }
  }
  useEffect(() => { if (data) load().catch(err => setError(err.message)); }, [revision]);
  function saveUser(event) {
    event.preventDefault();
    const payload = { display_name: editing.display_name, role: editing.role, department: editing.role === 'agent' ? editing.department : null, is_active: editing.is_active };
    const creating = !editing.id;
    if (creating) Object.assign(payload, { email: editing.email, password: editing.password });
    setPending({ title: creating ? 'ยืนยันสร้างบัญชีผู้ใช้' : 'ยืนยันแก้ไขบัญชีและสิทธิ์', message: `${editing.display_name} (${editing.email}) จะเป็น${ROLE[editing.role]}${editing.role === 'agent' ? `${DEPARTMENT_FULL[editing.department]}` : ''}${editing.is_active ? '' : ' และถูกระงับการใช้งาน'} การเปลี่ยนสิทธิ์จะยกเลิกเซสชันเดิม`, run: () => request(creating ? '/admin/users' : `/admin/users/${editing.id}`, { method: creating ? 'POST' : 'PUT', body: JSON.stringify(payload) }) });
  }
  const info = ADMIN_PAGES.find(item => item[0] === page);
  if (loading) return <div className="admin-loading"><div className="loading-orbit"/><p>กำลังโหลดพื้นที่ผู้ดูแล…</p></div>;
  if (!data) return <div className="admin-content"><p className="notice error">{error || 'โหลดข้อมูลไม่สำเร็จ'}</p><button className="primary" onClick={() => load().catch(err => setError(err.message))}>ลองอีกครั้ง</button></div>;
  const stats = data.overview;
  const filteredUsers = data.users.filter(user => (roleFilter === 'all' || user.role === roleFilter) && `${user.email} ${user.display_name}`.toLowerCase().includes(query.toLowerCase()));
  const filteredAudit = data.audit.filter(item => `${ACTION[item.action]} ${item.actor_email} ${item.target}`.toLowerCase().includes(query.toLowerCase()));
  return <div className="admin-content">
    <div className="admin-title"><div><h1>{info?.[1]}</h1><p>{({ overview: 'ดูภาพรวมบริการ จัดลำดับงาน และกระจายงานให้ทีม', users: 'ควบคุมบัญชี บทบาท และการเข้าถึงคิวของแต่ละฝ่าย', catalog: 'กำหนดชื่อบริการและเปิดรับคำขอของทั้ง 5 ฝ่าย', settings: 'ปรับพื้นที่ทำงานและนโยบายการรับคำขอขององค์กร', audit: 'ตรวจว่าใครเปลี่ยนอะไร และเมื่อไร' })[page]}</p></div><button className="secondary-button" disabled={busy} onClick={() => load().catch(err => setError(err.message))}><Icon name="history"/> อัปเดตข้อมูล</button></div>
    {error && <div className="admin-alert error" role="alert">{error}<button onClick={() => setError('')} aria-label="ปิดข้อผิดพลาด"><Icon name="close" size={18}/></button></div>}
    {success && <div className="admin-alert success" role="status"><Icon name="check"/>{success}</div>}
    {page === 'overview' && <>
      <div className="metric-grid" aria-label="สรุปคำขอทั้งองค์กร">{[['ทั้งหมด', stats.total], ['รอรับงาน', stats.open], ['กำลังดำเนินการ', stats.in_progress], ['เสร็จแล้ว', stats.done]].map(([label, count]) => <div className="metric" key={label}><span>{label}</span><strong>{count}</strong></div>)}</div>
      <div className="overview-work"><section className="admin-panel attention-panel"><div className="panel-heading"><div><h2>งานที่ต้องดูแล</h2><p>เลือกเพื่อเปิดคิวที่กรองแล้ว</p></div><Icon name="bell"/></div><button onClick={() => onOpenQueue('All', 'urgent')}><span><i className="attention-dot urgent"/>เร่งด่วนที่ยังไม่เสร็จ</span><b>{stats.urgent}</b><Icon name="arrow"/></button><button onClick={() => onOpenQueue('All', 'unassigned')}><span><i className="attention-dot"/>ยังไม่มีผู้รับผิดชอบ</span><b>{stats.unassigned}</b><Icon name="arrow"/></button><button onClick={() => onOpenQueue('All', 'aging')}><span><i className="attention-dot aging"/>เปิดเกิน {stats.aging_hours} ชั่วโมง</span><b>{stats.aging}</b><Icon name="arrow"/></button><small>เกณฑ์งานค้างเป็นสัญญาณเตือนภายใน ไม่ใช่ SLA</small></section>
      <section className="admin-panel department-panel"><div className="panel-heading"><div><h2>คิวบริการแต่ละฝ่าย</h2><p>ดูภาระงานและเปิดคิวของทีม</p></div></div>{stats.by_department.map(dept => <button className={`department-card ${dept.department.toLowerCase()}`} key={dept.department} onClick={() => onOpenQueue(dept.department)}><span className="department-monogram">{dept.department}</span><span className="department-information"><b>{DEPARTMENT_FULL[dept.department]}</b><small>{dept.total} ทั้งหมด · {dept.done} เสร็จแล้ว</small></span><span className="department-pending"><b>{dept.open}</b><small>ยังไม่เสร็จ</small></span><Icon name="arrow"/></button>)}<button className="text-button all-queues" onClick={() => onOpenQueue('All')}>เปิดกล่องงานทั้งหมด <Icon name="arrow"/></button></section></div>
      <section className="admin-panel trend-panel"><div className="panel-heading"><div><h2>คำขอใหม่ใน 7 วัน</h2><p>ปริมาณคำขอที่สร้างในแต่ละวัน · นับตามวันที่ UTC</p></div><span className="trend-total">{stats.daily.reduce((sum, day) => sum + day.count, 0)} คำขอ</span></div><div className="volume-chart" role="img" aria-label={stats.daily.map(d => `${d.date}: ${d.count} คำขอ`).join(', ')}>{stats.daily.map(d => <div key={d.date}><b>{d.count}</b><div className="chart-track"><i style={{ height: `${d.count / Math.max(1, ...stats.daily.map(x => x.count)) * 100}%` }}/></div><small>{new Date(`${d.date}T12:00:00Z`).toLocaleDateString('th-TH', { day: 'numeric', month: 'short' })}</small></div>)}</div></section>
    </>}
    {page === 'users' && <section className="admin-panel"><div className="panel-heading"><div><h2>บัญชีผู้ใช้ <span className="count-label">{data.users.length}</span></h2><p>{stats.active_users} บัญชีเปิดใช้งาน</p></div><button className="primary" onClick={() => { setError(''); setEditing({ display_name: '', email: '', password: '', role: 'employee', department: null, is_active: true }); }}><Icon name="plus"/> เพิ่มผู้ใช้</button></div><div className="admin-filters"><label className="search-box"><Icon name="search"/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="ค้นหาชื่อหรืออีเมล" aria-label="ค้นหาผู้ใช้"/></label><select value={roleFilter} onChange={e => setRoleFilter(e.target.value)} aria-label="กรองบทบาท"><option value="all">ทุกบทบาท</option>{Object.entries(ROLE).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></div><div className="table-scroll"><table className="admin-table"><thead><tr><th>ผู้ใช้</th><th>บทบาท / ฝ่าย</th><th>สถานะ</th><th>จัดการ</th></tr></thead><tbody>{filteredUsers.map(user => <tr key={user.id}><td><div className="table-user"><span className="avatar">{(user.display_name || user.email).slice(0, 2).toUpperCase()}</span><div><b>{user.display_name || user.email.split('@')[0]}</b><small>{user.email}{user.id === currentUser.id ? ' · คุณ' : ''}</small></div></div></td><td>{ROLE[user.role]}{user.department && <small>{DEPARTMENT_FULL[user.department]}</small>}</td><td><span className={`account-state ${user.is_active ? 'active' : ''}`}>{user.is_active ? 'ใช้งานอยู่' : 'ระงับ'}</span></td><td><button className="text-button" onClick={() => { setError(''); setEditing({ ...user, display_name: user.display_name || user.email.split('@')[0], password: '' }); }}>แก้ไข</button><button className="text-button" disabled={user.id === currentUser.id} onClick={() => { setError(''); setEditing({ ...user, mode: 'password', password: '' }); }}>รีเซ็ตรหัสผ่าน</button></td></tr>)}</tbody></table>{!filteredUsers.length && <div className="empty-state">ไม่พบบัญชีที่ตรงกับคำค้น</div>}</div></section>}
    {page === 'catalog' && <><div className="admin-info"><Icon name="catalog"/><p>ปิดหมวดเพื่อหยุดรับคำขอใหม่ได้ งานเดิมและประวัติยังอยู่ตามสิทธิ์เดิม งานส่งเข้าคิวตามหมวดและจำกัดสิทธิ์ตามฝ่าย</p></div><div className="catalog-grid">{data.catalog.map(item => <CategoryForm key={`${item.category}-${item.label}-${item.is_active}-${item.description}`} item={item} busy={busy} onSave={payload => setPending({ title: 'ยืนยันปรับหมวดบริการ', message: `${item.category} จะ${payload.is_active ? 'เปิด' : 'ปิด'}รับคำขอใหม่ และใช้ชื่อ “${payload.label}”`, run: () => request(`/admin/catalog/${item.category}`, { method: 'PUT', body: JSON.stringify(payload) }) })}/>)}</div></>}
    {page === 'settings' && <SettingsForm settings={data.settings} busy={busy} onSave={payload => setPending({ title: 'ยืนยันบันทึกการตั้งค่าระบบ', message: `การตั้งค่านี้มีผลทั้งองค์กร${!payload.accepting_tickets ? ' และจะหยุดรับ Ticket ใหม่ทุกหมวด งานเดิมยังดำเนินการต่อได้' : ''}`, run: () => request('/admin/settings', { method: 'PUT', body: JSON.stringify(payload) }) })}/>}
    {page === 'audit' && <section className="admin-panel"><div className="panel-heading"><h2>ประวัติล่าสุด <span className="count-label">{data.audit.length}</span></h2><span>ล่าสุดสูงสุด 200 เหตุการณ์</span></div><label className="search-box audit-search"><Icon name="search"/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="ค้นหาการทำรายการ ผู้ดูแล หรือเป้าหมาย" aria-label="ค้นหาประวัติผู้ดูแล"/></label><div className="audit-feed">{filteredAudit.map(item => <article key={item.id}><span className="audit-symbol"><Icon name="history"/></span><div><b>{ACTION[item.action] || item.action}</b><p>{item.actor_email} <span>·</span> {item.target}</p><details><summary>รายละเอียดการเปลี่ยนแปลง</summary><pre>{JSON.stringify(item.details, null, 2)}</pre></details></div><time>{time(item.created_at)}</time></article>)}{!filteredAudit.length && <div className="empty-state"><Icon name="shield" size={36}/><h3>ยังไม่มีรายการที่ตรงกัน</h3><p>การตั้งค่า บัญชี และการมอบหมายงานจะบันทึกที่นี่</p></div>}</div></section>}
    {editing && <Dialog title={editing.mode === 'password' ? 'รีเซ็ตรหัสผ่าน' : editing.id ? 'แก้ไขบัญชีผู้ใช้' : 'เพิ่มบัญชีผู้ใช้'} onClose={() => setEditing(null)} busy={busy}>
      {error && <p className="admin-alert error" role="alert">{error}</p>}
      {editing.mode === 'password' ? <form className="admin-form" onSubmit={event => { event.preventDefault(); setPending({ title: 'ยืนยันรีเซ็ตรหัสผ่าน', message: `เปลี่ยนรหัสผ่านของ ${editing.email} และยกเลิกเซสชันที่ Login อยู่ทั้งหมด`, run: () => request(`/admin/users/${editing.id}/reset-password`, { method: 'POST', body: JSON.stringify({ password: editing.password }) }) }); }}><p>{editing.email}</p><label>รหัสผ่านใหม่<input type="password" required minLength={10} maxLength={128} autoComplete="new-password" value={editing.password} onChange={e => setEditing({ ...editing, password: e.target.value })}/><small>อย่างน้อย 10 ตัวอักษร ส่งรหัสผ่านให้เจ้าของบัญชีผ่านช่องทางที่เหมาะสม</small></label><div className="admin-form-actions"><button type="button" className="secondary-button" onClick={() => setEditing(null)}>ยกเลิก</button><button className="primary" disabled={busy}>รีเซ็ตรหัสผ่าน</button></div></form> : <form className="admin-form" onSubmit={saveUser}><label>ชื่อที่แสดง<input required minLength={2} maxLength={100} value={editing.display_name} onChange={e => setEditing({ ...editing, display_name: e.target.value })}/></label><label>อีเมล<input type="email" required disabled={!!editing.id} value={editing.email} onChange={e => setEditing({ ...editing, email: e.target.value })}/></label>{!editing.id && <label>รหัสผ่านเริ่มต้น<input type="password" required minLength={10} maxLength={128} autoComplete="new-password" value={editing.password} onChange={e => setEditing({ ...editing, password: e.target.value })}/><small>อย่างน้อย 10 ตัวอักษร</small></label>}<div className="form-two-col"><label>บทบาท<select value={editing.role} disabled={editing.id === currentUser.id} onChange={e => setEditing({ ...editing, role: e.target.value, department: e.target.value === 'agent' ? 'IT' : null })}>{Object.entries(ROLE).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>{editing.role === 'agent' && <label>ฝ่าย<select value={editing.department} onChange={e => setEditing({ ...editing, department: e.target.value })}>{DEPARTMENT_CODES.map(code => <option key={code} value={code}>{DEPARTMENT_FULL[code]}</option>)}</select></label>}</div><label className="switch-line"><input type="checkbox" checked={editing.is_active} disabled={editing.id === currentUser.id} onChange={e => setEditing({ ...editing, is_active: e.target.checked })}/><span>เปิดใช้งานบัญชี<small>บัญชีที่ระงับจะ Login และใช้งาน API ไม่ได้</small></span></label><div className="admin-form-actions"><button type="button" className="secondary-button" onClick={() => setEditing(null)}>ยกเลิก</button><button className="primary" disabled={busy}>บันทึกผู้ใช้</button></div></form>}
    </Dialog>}
    {pending && <Dialog title={pending.title} onClose={() => setPending(null)} busy={busy} small><div className="confirm-icon"><Icon name="shield" size={28}/></div><p className="confirm-copy">{pending.message}</p><div className="admin-form-actions"><button type="button" className="secondary-button" disabled={busy} onClick={() => setPending(null)}>ยกเลิก</button><button className="primary" disabled={busy} onClick={() => perform(pending)}>{busy ? 'กำลังบันทึก…' : 'ยืนยัน'}</button></div></Dialog>}
  </div>;
}

function SettingsForm({ settings, busy, onSave }) {
  const [form, setForm] = useState(settings);
  useEffect(() => setForm(settings), [settings]);
  const update = (key, value) => setForm(current => ({ ...current, [key]: value }));
  return <form className="admin-panel admin-form settings-form" onSubmit={event => { event.preventDefault(); onSave(form); }}><div className="settings-section"><div><Icon name="settings"/><h2>พื้นที่ทำงาน</h2><p>ใช้ชื่อองค์กรเดียวกันในหน้า Login และ Sidebar</p></div><div><label>ชื่อองค์กร<input required minLength={2} maxLength={100} value={form.organization_name} onChange={e => update('organization_name', e.target.value)}/></label><label>ประกาศถึงผู้ใช้<textarea rows={3} maxLength={1000} value={form.announcement} onChange={e => update('announcement', e.target.value)} placeholder="เช่น แจ้งช่วงเวลาบริการหรือการบำรุงรักษา"/><small>เว้นว่างเพื่อซ่อนประกาศ</small></label></div></div><div className="settings-section"><div><Icon name="inbox"/><h2>การรับคำขอ</h2><p>พักการรับงานใหม่ได้ โดยผู้ใช้ยังติดตามงานเดิมได้</p></div><div><label className="switch-line"><input type="checkbox" checked={form.accepting_tickets} onChange={e => update('accepting_tickets', e.target.checked)}/><span>เปิดรับ Ticket ใหม่<small>{form.accepting_tickets ? 'พนักงานสร้างคำขอใหม่ได้' : 'หยุดรับคำขอใหม่ทุกหมวด'}</small></span></label><label>เกณฑ์เน้นงานค้าง (ชั่วโมง)<input type="number" required min={1} max={720} value={form.aging_hours} onChange={e => update('aging_hours', e.target.value === '' ? '' : Number(e.target.value))}/><small>ใช้กับ Dashboard และป้ายงานค้าง ไม่เปลี่ยนความเร่งด่วนอัตโนมัติ</small></label></div></div><div className="admin-form-actions"><span>ค่าบันทึกในฐานข้อมูลและคงอยู่หลังรีสตาร์ต</span><button className="primary" disabled={busy}>บันทึกการตั้งค่า</button></div></form>;
}

function CategoryForm({ item, busy, onSave }) {
  const [form, setForm] = useState({ label: item.label, description: item.description, is_active: item.is_active });
  return <form className={`admin-panel admin-form category-form ${item.category.toLowerCase()}`} onSubmit={event => { event.preventDefault(); onSave(form); }}><div className="panel-heading"><span className="department-monogram">{item.category}</span><div><h2>{DEPARTMENT_FULL[item.category]}</h2><p>ส่งเข้าคิว {item.category} อัตโนมัติ</p></div></div><label>ชื่อบริการ<input required minLength={2} maxLength={100} value={form.label} onChange={e => setForm({ ...form, label: e.target.value })}/></label><label>คำอธิบาย<textarea maxLength={500} rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}/></label><label className="switch-line"><input type="checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })}/><span>เปิดรับคำขอใหม่</span></label><button className="primary" disabled={busy}>บันทึกหมวด {item.category}</button></form>;
}
