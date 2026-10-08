import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './fonts.css';
import './style.css';
import './workspace.css';
import AdminWorkspace, { ADMIN_PAGES } from './admin';
import { Icon } from './icons';
import { DEPARTMENT, DEPARTMENT_FULL, DEPARTMENT_CODES } from './departments';
import { useRealtime } from './realtime';

const STATUS = {
  Open: { label: 'รอดำเนินการ', tone: 'open' },
  'In Progress': { label: 'กำลังดำเนินการ', tone: 'progress' },
  Done: { label: 'เสร็จแล้ว', tone: 'done' },
};
const ROLE = { employee: 'พนักงาน', agent: 'เจ้าหน้าที่', admin: 'ผู้ดูแลระบบ' };

function App() {
  const [auth, setAuth] = useState(null);
  const [view, setView] = useState('inbox');
  const [expanded, setExpanded] = useState(false);
  const [workspaceRevision, setWorkspaceRevision] = useState(0);
  const loadMessagesRef = useRef(null);
  const refreshEpoch = useRef(0);
  const activeTicketRef = useRef(null);
  const [settings, setSettings] = useState({ organization_name: 'บริษัท ตัวอย่าง จำกัด', announcement: '', accepting_tickets: true, aging_hours: 24 });
  const [users, setUsers] = useState([]);
  const [focusFilter, setFocusFilter] = useState('all');
  const [showNotifications, setShowNotifications] = useState(false);
  const [theme, setTheme] = useState(() => { try { return localStorage.getItem('ticketcenter-theme') === 'dark' ? 'dark' : 'light'; } catch { return 'light'; } });
  const searchRef = useRef(null);
  const composerRef = useRef(null);
  const [mobileDetail, setMobileDetail] = useState(false);
  const [isCompact, setIsCompact] = useState(() => window.matchMedia('(max-width: 900px)').matches);
  const [updatedAt, setUpdatedAt] = useState(null);

  const [email, setEmail] = useState('employee@example.test');
  const [password, setPassword] = useState('');
  const [tickets, setTickets] = useState([]);
  const [unreadCounts, setUnreadCounts] = useState({});
  const [messages, setMessages] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [catalog, setCatalog] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [messageDraft, setMessageDraft] = useState('');
  const [messagesBusy, setMessagesBusy] = useState(false);
  const [messagesError, setMessagesError] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [impact, setImpact] = useState('');
  const [category, setCategory] = useState('IT');
  const [query, setQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterDepartment, setFilterDepartment] = useState('All');
  const [showComposer, setShowComposer] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [now, setNow] = useState(Date.now());
  useModalFocus(composerRef, showComposer, () => setShowComposer(false), busy);

  async function request(path, options = {}, token = auth?.access_token) {
    const response = await fetch(`/api${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
    });
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && token) { setAuth(null); setView('inbox'); setShowComposer(false); setConfirmation(null); setError('เซสชันหมดอายุหรือสิทธิ์เปลี่ยน กรุณาเข้าสู่ระบบใหม่'); }
    if (!response.ok) {
      const detail = typeof body.detail === 'string' ? body.detail : `กรุณาตรวจข้อมูล (${response.status})`;
      const translations = { 'Email already exists': 'อีเมลนี้มีบัญชีแล้ว', 'New requests are temporarily paused': 'ระบบพักการรับคำขอใหม่ชั่วคราว', 'This service is temporarily unavailable': 'หมวดนี้พักการรับคำขอใหม่ชั่วคราว', 'Invalid credentials': 'อีเมลหรือรหัสผ่านไม่ถูกต้อง หรือบัญชีถูกระงับ', 'Session expired or account disabled. Please sign in again': 'เซสชันหมดอายุหรือสิทธิ์เปลี่ยน กรุณาเข้าสู่ระบบใหม่', "Reassign unfinished tickets before changing this account's access": 'กรุณามอบหมายงานที่ยังไม่เสร็จให้คนอื่นก่อนเปลี่ยนสิทธิ์หรือระงับบัญชีนี้', "Choose an active agent from the ticket's department": 'กรุณาเลือกเจ้าหน้าที่ที่เปิดใช้งานในฝ่ายเดียวกับ Ticket', 'Only employees can create tickets': 'เฉพาะพนักงานเท่านั้นที่สร้างคำขอได้' };
      throw new Error(translations[detail] || detail);
    }
    return body;
  }
  async function refresh(token = auth?.access_token) {
    const epoch = ++refreshEpoch.current;
    const [items, counts, unread] = await Promise.all([request('/tickets', {}, token), request('/dashboard', {}, token), request('/unread-counts', {}, token)]);
    if (epoch !== refreshEpoch.current) return;
    setTickets(items);
    setDashboard(counts);
    setUnreadCounts(unread);
    setUpdatedAt(new Date());
    setSelectedId(current => items.some(ticket => ticket.id === current) ? current : items[0]?.id ?? null);
  }
  async function refreshSettings(token = auth?.access_token) {
    const [configuration, services] = await Promise.all([request(token ? '/settings' : '/branding', {}, token), request('/catalog', {}, null)]);
    setSettings(current => ({ ...current, ...configuration })); setCatalog(services);
    setCategory(current => services.some(service => service.category === current) ? current : services[0]?.category || '');
  }
  async function adminChangesApplied() {
    await refreshSettings();
    const user = await request('/me'); setAuth(current => ({ ...current, user }));
    await refresh();
  }
  function openQueue(department = 'All', focus = 'all') { setView('inbox'); setMobileDetail(false); setFilterDepartment(department); setFilterStatus('All'); setFocusFilter(focus); setQuery(''); }
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('ticketcenter-theme', theme); } catch {}
  }, [theme]);
  useEffect(() => {
    function keydown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k' && auth && !showComposer && !confirmation && !document.querySelector('[aria-modal="true"]')) {
        event.preventDefault(); setView('inbox'); setMobileDetail(false); window.setTimeout(() => searchRef.current?.focus(), 0);
      }
    }
    window.addEventListener('keydown', keydown); return () => window.removeEventListener('keydown', keydown);
  }, [auth, showComposer, confirmation]);
  useEffect(() => {
    const media = window.matchMedia('(max-width: 900px)');
    const update = () => setIsCompact(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  useEffect(() => {
    const health = () => request('/health', {}, null).then(() => setApiOnline(true)).catch(() => setApiOnline(false));
    health();
    const heartbeat = window.setInterval(health, 15000);
    refreshSettings().catch(() => {});
    const timer = window.setInterval(() => setNow(Date.now()), 60_000);
    return () => { window.clearInterval(timer); window.clearInterval(heartbeat); };
  }, []);
  useEffect(() => {
    if (auth?.user.role === 'admin') request('/admin/users').then(setUsers).catch(() => {});
  }, [auth?.access_token]);
  useEffect(() => {
    if (!confirmation) return;
    const closeOnEscape = event => { if (event.key === 'Escape' && !busy) setConfirmation(null); };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [confirmation, busy]);

  async function login(event) {
    event.preventDefault(); setError(''); setBusy(true);
    try {
      const result = await request('/login', { method: 'POST', body: JSON.stringify({ email, password }) }, null);
      setAuth(result); setView(result.user.role === 'admin' ? 'overview' : 'inbox'); setPassword(''); setNotice('');
      await refreshSettings(result.access_token);
      await refresh(result.access_token);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  async function createTicket(event) {
    event.preventDefault(); setError(''); setNotice(''); setBusy(true);
    try {
      const ticket = await request('/tickets', { method: 'POST', body: JSON.stringify({ title, description, impact, category }) });
      setTitle(''); setDescription(''); setImpact(''); setShowComposer(false); await refresh(); setSelectedId(ticket.id); setMobileDetail(true);
      setNotice(`สร้าง Ticket #${ticket.id} และส่งเข้าคิว ${ticket.department} แล้ว`);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  async function changeStatus(ticket) {
    const next = ticket.status === 'Open' ? 'In Progress' : 'Done';
    setError(''); setNotice(''); setBusy(true);
    try {
      await request(`/tickets/${ticket.id}/status`, { method: 'PATCH', body: JSON.stringify({ status: next }) });
      await refresh(); setNotice(`อัปเดต Ticket #${ticket.id} เป็น ${STATUS[next].label} แล้ว`);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  async function changePriority(ticket, nextPriority) {
    if (!nextPriority || nextPriority === ticket.priority) return;
    setError(''); setNotice(''); setBusy(true);
    try {
      await request(`/tickets/${ticket.id}/priority`, { method: 'PATCH', body: JSON.stringify({ priority: nextPriority }) });
      await refresh();
      setNotice(`ปรับ Ticket #${ticket.id} เป็น${nextPriority === 'Urgent' ? 'เร่งด่วน' : 'ปกติ'}แล้ว`);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  function askStatusChange(ticket) {
    setConfirmation({ type: 'status', ticket });
  }
  async function confirmPendingAction() {
    const pending = confirmation;
    setConfirmation(null);
    if (!pending) return;
    if (pending.type === 'logout') logout();
    else if (pending.type === 'status') await changeStatus(pending.ticket);
    else if (pending.type === 'priority') await changePriority(pending.ticket, pending.priority);
    else if (pending.type === 'assignment') {
      setBusy(true); setError('');
      try { await request(`/admin/tickets/${pending.ticket.id}/assignee`, { method: 'PATCH', body: JSON.stringify({ assignee_id: pending.assignee_id }) }); await refresh(); setNotice('มอบหมายผู้รับผิดชอบแล้ว'); } catch (err) { setError(err.message); } finally { setBusy(false); }
    }
  }
  async function sendMessage(event) {
    event.preventDefault();
    const body = messageDraft.trim();
    if (!body || !selectedTicket) return;
    setMessagesError(''); setMessagesBusy(true);
    try {
      const ticketId = selectedTicket.id;
      const message = await request(`/tickets/${ticketId}/messages`, { method: 'POST', body: JSON.stringify({ body }) });
      if (activeTicketRef.current === ticketId) {
        setMessages(current => [...new Map([...current, message].map(item => [item.id, item])).values()].sort((a, b) => a.id - b.id));
        setUnreadCounts(current => ({ ...current, [ticketId]: 0 })); setMessageDraft('');
      }
    } catch (err) { setMessagesError(err.message); } finally { setMessagesBusy(false); }
  }
  function logout() {
    refreshEpoch.current += 1;
    setAuth(null); setTickets([]); setDashboard(null); setSelectedId(null); setNotice('ออกจากระบบแล้ว');
    setQuery(''); setFilterStatus('All'); setFilterDepartment('All');
    setView('inbox'); setExpanded(false); setUsers([]); setFocusFilter('all'); setShowNotifications(false); setShowComposer(false);
  }

  const visibleTickets = useMemo(() => {
    const term = query.trim().toLocaleLowerCase();
    const filtered = tickets.filter(ticket => {
      const matchesQuery = !term || String(ticket.id).includes(term) || ticket.title.toLocaleLowerCase().includes(term) || ticket.description.toLocaleLowerCase().includes(term);
      const matchesFocus = focusFilter === 'all' || (ticket.status !== 'Done' && ((focusFilter === 'urgent' && ticket.priority === 'Urgent') || (focusFilter === 'unassigned' && !ticket.assignee_id) || (focusFilter === 'aging' && now - new Date(ticket.created_at).getTime() >= settings.aging_hours * 3600000)));
      return matchesQuery && matchesFocus && (filterStatus === 'All' || ticket.status === filterStatus) && (filterDepartment === 'All' || ticket.department === filterDepartment);
    });
    if (auth?.user.role === 'agent' || auth?.user.role === 'admin') {
      return filtered.sort((a, b) => Number(b.priority === 'Urgent') - Number(a.priority === 'Urgent') || new Date(a.created_at) - new Date(b.created_at));
    }
    return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }, [tickets, query, filterStatus, filterDepartment, auth, focusFilter, settings.aging_hours, now]);
  const selectedTicket = visibleTickets.find(ticket => ticket.id === selectedId) || visibleTickets[0] || null;
  activeTicketRef.current = view === 'inbox' && (!isCompact || mobileDetail) ? selectedTicket?.id : null;
  useEffect(() => {
    if (!auth?.access_token || !selectedTicket?.id || view !== 'inbox' || (isCompact && !mobileDetail)) { setMessages([]); return; }
    let cancelled = false;
    setMessages([]); setMessagesBusy(true); setMessagesError(''); setMessageDraft('');
    const loadMessages = async (initial = false) => {
      try {
        const items = await request(`/tickets/${selectedTicket.id}/messages`);
        await request(`/tickets/${selectedTicket.id}/messages/read`, { method: 'POST' });
        if (!cancelled) {
          setMessages(current => [...new Map([...current, ...items].map(item => [item.id, item])).values()].sort((a, b) => a.id - b.id));
          setUnreadCounts(current => ({ ...current, [selectedTicket.id]: 0 }));
        }
      } catch (err) { if (!cancelled) setMessagesError(err.message); }
      finally { if (!cancelled && initial) setMessagesBusy(false); }
    };
    loadMessages(true);
    loadMessagesRef.current = () => loadMessages(false);
    return () => { cancelled = true; loadMessagesRef.current = null; };
  }, [auth?.access_token, selectedTicket?.id, view, isCompact, mobileDetail]);
  const realtimeStatus = useRealtime(auth?.access_token, event => {
    if (event.type === 'read.updated') {
      request('/unread-counts').then(setUnreadCounts).catch(() => {});
      return;
    }
    refresh().catch(err => setError(err.message));
    if (event.type === 'ready' || event.type === 'workspace.updated') {
      refreshSettings().catch(() => {});
      setWorkspaceRevision(current => current + 1);
      if (auth?.user.role === 'admin') request('/admin/users').then(setUsers).catch(() => {});
    } else if (event.type === 'ticket.updated') setWorkspaceRevision(current => current + 1);
    if (event.type === 'ready' || (event.type === 'message.created' && event.ticket_id === selectedTicket?.id)) {
      loadMessagesRef.current?.();
    }
  }, () => {
    logout(); setError('เซสชันหมดอายุหรือสิทธิ์เปลี่ยน กรุณาเข้าสู่ระบบใหม่');
  });
  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(''), 5000);
    return () => window.clearTimeout(timer);
  }, [notice]);
  const counts = useMemo(() => ({
    total: tickets.length,
    Open: tickets.filter(t => t.status === 'Open').length,
    'In Progress': tickets.filter(t => t.status === 'In Progress').length,
    Done: tickets.filter(t => t.status === 'Done').length,
  }), [tickets]);
  const initials = auth?.user.email.split('@')[0].split(/[._-]/).map(part => part[0]).join('').slice(0, 2).toUpperCase();

  const unreadTotal = Object.values(unreadCounts).reduce((sum, n) => sum + n, 0);
  return <div className={`app-shell department-${auth?.user.department?.toLowerCase() || auth?.user.role || 'welcome'} ${expanded ? 'workspace-expanded' : ''}`}>
    {!auth ? <main className="login-screen">
      <section className="login-brand"><a className="brand" href="#top"><span className="brand-mark">T</span><span>TicketCenter<small>ศูนย์บริการภายในองค์กร</small></span></a><div className="login-copy"><h1>แจ้งเรื่องเดียว<br/>ติดตามได้จนจบ</h1><p>เชื่อมพนักงานกับทีมที่ดูแลปัญหา<br/>โดยไม่ต้องตามงานหลายช่องทาง</p><div className="login-service-list">{DEPARTMENT_CODES.map(code => <div key={code}><span className={`department-monogram ${code.toLowerCase()}`}>{code}</span><span><b>{DEPARTMENT_FULL[code]}</b></span></div>)}</div><p className="login-track"><Icon name="check"/> แจ้งปัญหา <Icon name="arrow"/> ทีมรับงาน <Icon name="arrow"/> ติดตามผล</p></div><div className="login-foot">{settings.organization_name}</div></section>
      <section className="login-side"><div className="login-card"><h2>เข้าสู่ระบบ</h2><p>พื้นที่ทำงานของ {settings.organization_name}</p><form onSubmit={login}><label>อีเมล<input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="name@company.com" autoComplete="username"/></label><label>รหัสผ่าน<input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="กรอกรหัสผ่าน" autoComplete="current-password"/></label>{error && <p className="error-inline" role="alert">{error}</p>}<button className="primary full" disabled={busy}>{busy ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'} <Icon name="arrow"/></button></form><div className="demo-hint"><Icon name="shield"/><span><b>เข้าถึงตามบทบาทของคุณ</b><small>พนักงาน · เจ้าหน้าที่แต่ละฝ่าย · ผู้ดูแลระบบ</small><small>ใช้บัญชีที่ผู้ดูแลจัดเตรียมให้</small></span></div></div><div className="login-api"><i className={apiOnline ? 'up' : ''}/> {apiOnline ? 'เชื่อมต่อระบบบริการแล้ว' : 'กำลังตรวจการเชื่อมต่อ'}</div></section>
    </main> : <>
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="TicketCenter"><span className="brand-mark">T</span><span>TicketCenter<small>SERVICE DESK</small></span></a>
        <div className="workspace-switch"><span className="workspace-icon">TC</span><span><b>{settings.organization_name}</b><small>Internal workspace</small></span></div>
        {auth.user.role === 'admin' && <><div className="side-label">พื้นที่ผู้ดูแล</div>{ADMIN_PAGES.map(([id, label, icon]) => <button key={id} className={`nav-link admin-nav ${view === id ? 'active' : ''}`} onClick={() => setView(id)}><Icon name={icon}/>{label}</button>)}</>}
        <div className="side-label">กล่องงาน</div>
        <button className={`nav-link inbox-nav ${view === 'inbox' && filterStatus === 'All' ? 'active' : ''}`} onClick={() => { setView('inbox'); setFocusFilter('all'); setFilterStatus('All'); } }><Icon name="inbox"/> ทั้งหมด <b>{counts.total}</b></button>
        <button className={`nav-link ${view === 'inbox' && filterStatus === 'Open' ? 'active' : ''}`} onClick={() => { setView('inbox'); setFocusFilter('all'); setFilterStatus('Open'); } }><Icon name="clock"/> รอดำเนินการ <b>{counts.Open}</b></button>
        <button className={`nav-link ${view === 'inbox' && filterStatus === 'In Progress' ? 'active' : ''}`} onClick={() => { setView('inbox'); setFocusFilter('all'); setFilterStatus('In Progress'); } }><Icon name="history"/> กำลังดำเนินการ <b>{counts['In Progress']}</b></button>
        <button className={`nav-link ${view === 'inbox' && filterStatus === 'Done' ? 'active' : ''}`} onClick={() => { setView('inbox'); setFocusFilter('all'); setFilterStatus('Done'); } }><Icon name="check"/> เสร็จแล้ว <b>{counts.Done}</b></button>
        {auth.user.role === 'agent' && <><div className="side-label dept-label">คิวของฉัน</div><div className="nav-link queue-link active" title={DEPARTMENT_FULL[auth.user.department]}><span className={`dept-dot ${auth.user.department.toLowerCase()}`}/><span className="queue-name"><b>{DEPARTMENT_FULL[auth.user.department]}</b><small>คิวบริการของคุณ</small></span><b>{counts.total}</b></div></>}
        {auth.user.role === 'admin' && <><div className="side-label dept-label">คิวบริการ · ทุกฝ่าย</div>{DEPARTMENT_CODES.map(code => <button key={code} className={`nav-link queue-link ${filterDepartment === code && view === 'inbox' ? 'active' : ''}`} onClick={() => openQueue(filterDepartment === code && view === 'inbox' ? 'All' : code)} title={DEPARTMENT_FULL[code]}><span className={`dept-dot ${code.toLowerCase()}`}/><span className="queue-name"><b>{DEPARTMENT_FULL[code]}</b></span><b>{dashboard?.by_department[code] ?? 0}</b></button>)}</>}

        <div className="sidebar-bottom"><Icon name="shield" size={18}/><span>พื้นที่ทำงานปลอดภัย<small>เข้าถึงข้อมูลตามสิทธิ์ของบัญชี</small></span></div>
      </aside>
      <main className="main-area" id="top">
        <header className="topbar"><div className="mobile-brand"><span className="brand-mark">T</span> TicketCenter</div><div className="crumb">Workspace <span>/</span> {auth.user.role === 'employee' ? 'คำขอของฉัน' : auth.user.role === 'agent' ? DEPARTMENT_FULL[auth.user.department] : view === 'inbox' ? 'กล่องงานทุกฝ่าย' : ADMIN_PAGES.find(item => item[0] === view)?.[1]}</div><div className="top-actions"><button className="icon-button expand-toggle" aria-label={expanded ? 'คืนมุมมองปกติ' : 'ขยายพื้นที่ทำงาน'} aria-pressed={expanded} title={expanded ? 'คืนมุมมองปกติ' : 'ขยายพื้นที่ทำงาน'} onClick={() => setExpanded(!expanded)}><Icon name={expanded ? 'collapse' : 'expand'}/></button><button className="icon-button theme-toggle" aria-label={theme === 'light' ? 'เปลี่ยนเป็นธีมมืด' : 'เปลี่ยนเป็นธีมสว่าง'} title="สลับธีม" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}><Icon name={theme === 'light' ? 'moon' : 'sun'}/></button><div className="notification-wrap"><button className="icon-button" aria-label={`ข้อความที่ยังไม่อ่าน ${unreadTotal} ข้อความ`} aria-expanded={showNotifications} onClick={() => setShowNotifications(!showNotifications)}><Icon name="bell"/>{unreadTotal > 0 && <span className="notification-number">{unreadTotal}</span>}</button>{showNotifications && <div className="notification-menu"><b>ข้อความที่ยังไม่อ่าน</b>{tickets.filter(t => unreadCounts[t.id] > 0).map(t => <button key={t.id} onClick={() => { openQueue(); setSelectedId(t.id); setMobileDetail(true); setShowNotifications(false); }}><span>TC-{String(t.id).padStart(4, '0')}<small>{t.title}</small></span><b>{unreadCounts[t.id]}</b></button>)}{unreadTotal === 0 && <p>อ่านครบแล้ว พร้อมดูแลงานต่อ</p>}</div>}</div><span className={`api-pill ${apiOnline ? 'online' : 'offline'}`}><i/> {apiOnline ? 'ระบบปกติ' : 'เชื่อมต่อ API'}</span><button className="icon-button" aria-label="รีเฟรชรายการ" title="รีเฟรชรายการ" onClick={() => refresh().catch(e => setError(e.message))}><Icon name="history"/></button><div className="user-profile"><span className="avatar">{initials}</span><span><b>{auth.user.display_name || auth.user.email.split('@')[0]}</b><small>{ROLE[auth.user.role]}{auth.user.department ? ` · ${DEPARTMENT_FULL[auth.user.department]}` : ''}</small></span><button className="logout-button" onClick={() => setConfirmation({ type: 'logout' })} aria-label="ออกจากระบบ" title="ออกจากระบบ"><Icon name="logout"/></button></div></div></header>
        {settings.announcement && <div className="workspace-announcement" role="status"><Icon name="bell"/><span>{settings.announcement}</span></div>}
        {!settings.accepting_tickets && <div className="paused-banner">พักการรับคำขอใหม่ชั่วคราว คุณยังติดตามและดำเนินงานเดิมได้</div>}
        {auth.user.role === 'admin' && view !== 'inbox' ? <AdminWorkspace page={view} revision={workspaceRevision} request={request} currentUser={auth.user} onSettingsChanged={adminChangesApplied} onUsersChanged={setUsers} onOpenQueue={openQueue}/> : <>
        <div className="toolbar"><div><h1>{auth.user.role === 'employee' ? 'คำขอของฉัน' : auth.user.role === 'agent' ? `คิวบริการ · ${DEPARTMENT_FULL[auth.user.department]}` : 'ภาพรวมการให้บริการ'}</h1><p className="toolbar-description">{auth.user.role === 'employee' ? 'ติดตามคำขอบริการที่คุณแจ้งไว้' : auth.user.role === 'agent' ? `รายการและตัวเลขด้านล่างแสดงเฉพาะ ${DEPARTMENT_FULL[auth.user.department]}` : 'ติดตามและจัดลำดับงานของทั้ง 5 ฝ่าย'}</p></div><div className="toolbar-right">{auth.user.role === 'employee' && <button className="primary create-trigger" disabled={!settings.accepting_tickets || !catalog.length} onClick={() => setShowComposer(true)}><Icon name="plus"/> แจ้งคำขอใหม่</button>}</div></div>
        <section className="workspace-metrics" aria-label="สรุปคำขอ">{[['All', 'ทั้งหมด', counts.total, 'grid'], ['Open', 'รอรับงาน', counts.Open, 'inbox'], ['In Progress', 'กำลังดำเนินการ', counts['In Progress'], 'history'], ['Done', 'เสร็จแล้ว', counts.Done, 'check']].map(([id, label, value, icon]) => <button key={id} className={`workspace-metric ${filterStatus === id ? 'selected' : ''}`} onClick={() => { setFilterStatus(id); setFocusFilter('all'); }}><span><Icon name={icon}/>{label}</span><strong>{value}</strong></button>)}</section>
        {error && <div className="notice error" role="alert"><span>!</span>{error}<button onClick={() => setError('')} aria-label="ปิด"><Icon name="close" size={18}/></button></div>}{notice && <div className="notice success" role="status"><Icon name="check" size={18}/>{notice}<button onClick={() => setNotice('')} aria-label="ปิด"><Icon name="close" size={18}/></button></div>}
        <section className={`inbox-layout ${mobileDetail ? 'show-detail' : 'show-list'}`}>
          <div className="list-pane"><div className="list-toolbar"><label className="search-box"><Icon name="search"/><input ref={searchRef} value={query} onChange={e => setQuery(e.target.value)} placeholder="ค้นหา Ticket หรือหัวข้อ…" aria-label="ค้นหา Ticket"/><kbd>Ctrl K</kbd></label><div className="list-tools">{focusFilter !== 'all' && <button className="focus-filter" onClick={() => setFocusFilter('all')}>{({ urgent: 'เร่งด่วน', aging: 'งานค้าง', unassigned: 'ยังไม่มอบหมาย' })[focusFilter]} <Icon name="close" size={13}/></button>}<span>{visibleTickets.length} รายการ</span>{auth.user.role === 'admin' && <select value={filterDepartment} onChange={e => setFilterDepartment(e.target.value)} aria-label="กรองตามฝ่าย"><option value="All">ทุกฝ่าย</option>{DEPARTMENT_CODES.map(code => <option key={code} value={code}>{DEPARTMENT_FULL[code]}</option>)}</select>}<select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} aria-label="กรองตามสถานะ"><option value="All">ทุกสถานะ</option>{Object.entries(STATUS).map(([value, item]) => <option key={value} value={value}>{item.label}</option>)}</select></div></div>
            <div className="ticket-list">{visibleTickets.length ? visibleTickets.map(ticket => <TicketRow key={ticket.id} ticket={ticket} unreadCount={unreadCounts[ticket.id] || 0} selected={selectedTicket?.id === ticket.id} agingHours={settings.aging_hours} now={now} onClick={() => { setSelectedId(ticket.id); setMobileDetail(true); }}/>) : <div className="empty-state"><Icon name="search" size={32}/><h3>ไม่พบ Ticket</h3><p>{query ? 'ลองเปลี่ยนคำค้นหาหรือตัวกรอง' : 'เมื่อมีคำขอใหม่ รายการจะแสดงที่นี่'}</p></div>}</div>
            <div className="list-footer">อัปเดต {updatedAt?.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' }) || '…'} <span>·</span> เรียงตาม {auth.user.role === 'employee' ? 'ใหม่ล่าสุด' : 'เร่งด่วนและเก่าที่สุด'}</div>
          </div>
          <section className="detail-pane"><button className="back-to-list" onClick={() => setMobileDetail(false)}><Icon name="back"/> กลับไปรายการคำขอ</button>{selectedTicket ? <TicketDetail ticket={selectedTicket} role={auth.user.role} users={users} onAssign={(ticket, assignee_id) => setConfirmation({ type: 'assignment', ticket, assignee_id, assignee_name: users.find(u => u.id === assignee_id)?.display_name || users.find(u => u.id === assignee_id)?.email })} currentUserId={auth.user.id} realtimeStatus={realtimeStatus} busy={busy} onRequestStatusChange={askStatusChange} onChangePriority={(ticket, priority) => setConfirmation({ type: 'priority', ticket, priority })} messages={messages} messagesBusy={messagesBusy} messagesError={messagesError} messageDraft={messageDraft} setMessageDraft={setMessageDraft} onSendMessage={sendMessage} onRefreshMessages={() => { setMessagesBusy(true); request(`/tickets/${selectedTicket.id}/messages`).then(items => request(`/tickets/${selectedTicket.id}/messages/read`, { method: 'POST' }).then(() => { setMessages(items); setUnreadCounts(current => ({ ...current, [selectedTicket.id]: 0 })); })).catch(e => setMessagesError(e.message)).finally(() => setMessagesBusy(false)); }}/> : <div className="detail-empty"><Icon name="inbox" size={40}/><h2>เลือก Ticket เพื่อดูรายละเอียด</h2><p>สถานะ ผู้แจ้ง และประวัติการดำเนินงานจะแสดงในส่วนนี้</p></div>}</section>
        </section>
        <footer className="app-footer"><span>TicketCenter <b>·</b> Internal Service Desk</span><span>{settings.organization_name}</span></footer>
      </>}
      </main>
      {showComposer && <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && !busy && setShowComposer(false)}><section ref={composerRef} className="composer-modal" role="dialog" aria-modal="true" aria-labelledby="composer-title"><div className="modal-heading"><div><h2 id="composer-title">แจ้งคำขอบริการ</h2><p>ระบบจะส่งคำขอเข้าคิวของฝ่ายที่เลือกโดยอัตโนมัติ</p></div><button className="close-button" onClick={() => setShowComposer(false)} disabled={busy} aria-label="ปิด"><Icon name="close" size={18}/></button></div>{error && <div className="error-inline" role="alert">{error}</div>}<form className="create-form" onSubmit={createTicket}><label>หมวดบริการ<select value={category} onChange={e => setCategory(e.target.value)}>{catalog.map(c => <option key={c.category} value={c.category}>{c.category} · {c.label}</option>)}</select><small className="priority-guidance">{catalog.find(c => c.category === category)?.description}</small></label><label className="wide">หัวข้อ<input required minLength="3" maxLength="160" value={title} onChange={e => setTitle(e.target.value)} placeholder="สรุปปัญหาสั้น ๆ"/></label><label className="wide">ผลกระทบที่เกิดขึ้น<textarea required minLength="3" maxLength="2000" value={impact} onChange={e => setImpact(e.target.value)} placeholder="ใครได้รับผลกระทบ งานใดหยุดชะงัก และเกิดขึ้นบ่อยแค่ไหน"/></label><label className="wide">รายละเอียด<textarea required minLength="3" value={description} onChange={e => setDescription(e.target.value)} placeholder="อธิบายปัญหาและสิ่งที่ต้องการให้ทีมช่วยเหลือ"/></label><div className="form-footer"><span>คิวปลายทาง <b>{category}</b> · {DEPARTMENT[category]} <small className="priority-guidance">ระดับเริ่มต้น: ปกติ · เจ้าหน้าที่จะประเมินจากผลกระทบ</small></span><button className="primary" disabled={busy}>{busy ? 'กำลังส่ง…' : 'ส่งคำขอ'} <Icon name="arrow"/></button></div></form></section></div>}
      {confirmation && <ConfirmDialog confirmation={confirmation} busy={busy} onCancel={() => setConfirmation(null)} onConfirm={confirmPendingAction}/>}
    </>}

  </div>;
}

function ageText(createdAt, now) {
  const hours = Math.max(0, Math.floor((now - new Date(createdAt).getTime()) / 3_600_000));
  if (hours < 1) return 'ไม่ถึง 1 ชม.';
  if (hours < 24) return `${hours} ชม.`;
  return `${Math.floor(hours / 24)} วัน`;
}
function TicketRow({ ticket, unreadCount, selected, now, onClick, agingHours }) {
  const state = STATUS[ticket.status] || STATUS.Open;
  return <button className={`ticket-row ${selected ? 'selected' : ''}`} aria-current={selected ? 'true' : undefined} onClick={onClick}>
    <span className={`row-avatar ${ticket.department.toLowerCase()}`}>{ticket.department}</span><span className="row-content"><span className="row-top"><b>{ticket.title}</b><span className="row-trailing">{unreadCount > 0 && <span className="unread-badge" title={`${unreadCount} ข้อความที่ยังไม่ได้อ่าน`} aria-label={`${unreadCount} ข้อความที่ยังไม่ได้อ่าน`}>{unreadCount}</span>}<time>{ageText(ticket.created_at, now)}</time></span></span><span className="row-preview">{ticket.description}</span><span className="row-meta"><span className="ticket-ref">TC-{String(ticket.id).padStart(4, '0')}</span><span className={`mini-status ${state.tone}`}><i/>{state.label}</span>{ticket.priority === 'Urgent' && <span className="mini-priority">เร่งด่วน</span>}{ticket.status !== 'Done' && now - new Date(ticket.created_at).getTime() >= agingHours * 3600000 && <span className="aging-label">ค้างนาน</span>}<span className="row-dept">{ticket.department}</span></span></span>
  </button>;
}
function TicketDetail({ ticket, role, users, onAssign, currentUserId, realtimeStatus, busy, onRequestStatusChange, onChangePriority, messages, messagesBusy, messagesError, messageDraft, setMessageDraft, onSendMessage, onRefreshMessages }) {
  const feedRef = useRef(null);
  useEffect(() => { if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight; }, [ticket.id, messages.length]);
  const state = STATUS[ticket.status] || STATUS.Open;
  const canUpdate = (role === 'agent' || role === 'admin') && ticket.status !== 'Done';
  const canSetPriority = role === 'admin' || role === 'agent';
  const activities = [
    ...ticket.history.map(item => ({ ...item, kind: 'status' })),
    ...(ticket.priority_history || []).map(item => ({ ...item, kind: 'priority' })),
  ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  return <>
    <div className="detail-header"><div><div className="detail-ref">TC-{String(ticket.id).padStart(4, '0')} <span>·</span> {DEPARTMENT_FULL[ticket.department]}</div><h2>{ticket.title}</h2><div className="detail-badges"><span className={`mini-status ${state.tone}`}><i/>{state.label}</span>{canSetPriority ? <label className={`priority-control ${ticket.priority === 'Urgent' ? 'urgent' : 'normal'}`}><span>ความเร่งด่วน</span><select value={ticket.priority} disabled={busy} onChange={event => onChangePriority(ticket, event.target.value)} aria-label="กำหนดระดับความเร่งด่วน"><option value="Normal">ปกติ</option><option value="Urgent">เร่งด่วน</option></select></label> : <span className={`priority-badge ${ticket.priority === 'Urgent' ? 'urgent' : 'normal'}`}>{ticket.priority === 'Urgent' ? 'เร่งด่วน' : 'ปกติ'}</span>}</div></div><span className={`department-stamp ${ticket.department.toLowerCase()}`}>{ticket.department}</span></div>
    <div className="ticket-context"><div className="requester-avatar">{`U${ticket.employee_id}`}</div><div className="requester-info"><b>พนักงานผู้แจ้ง</b><small>พนักงาน #{ticket.employee_id} <span>·</span> แจ้งเมื่อ {new Date(ticket.created_at).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })}</small></div><span className="age-chip">เปิดมา {ageText(ticket.created_at, Date.now())}</span></div>
    <div className="detail-body"><details className="request-details"><summary><span>รายละเอียดและผู้รับผิดชอบ<small>{ticket.impact || ticket.description}</small></span><Icon name="chevron" size={18}/></summary><ol className="ticket-journey" aria-label="ขั้นตอนคำขอ">{['Open', 'In Progress', 'Done'].map((status, index) => <li key={status} className={index <= ['Open', 'In Progress', 'Done'].indexOf(ticket.status) ? 'reached' : ''}><span>{index + 1}</span>{STATUS[status].label}</li>)}</ol><div className="assignment-line"><span><Icon name="users"/>ผู้รับผิดชอบ <b>{ticket.assignee_name || `คิว ${DEPARTMENT_FULL[ticket.department]} · ยังไม่มอบหมาย`}</b></span>{role === 'admin' && ticket.status !== 'Done' && <select aria-label="มอบหมายเจ้าหน้าที่" value={ticket.assignee_id || ''} disabled={busy} onChange={e => onAssign(ticket, e.target.value ? Number(e.target.value) : null)}><option value="">ยังไม่มอบหมาย</option>{users.filter(u => u.is_active && u.role === 'agent' && u.department === ticket.department).map(u => <option key={u.id} value={u.id}>{u.display_name || u.email}</option>)}</select>}</div><div className="message-card"><div className="message-heading"><span>รายละเอียดคำขอ</span><span>{DEPARTMENT_FULL[ticket.department] || ticket.department}</span></div><p>{ticket.description}</p><div className="impact-summary"><b>ผลกระทบที่แจ้ง</b><p>{ticket.impact || 'ไม่มีข้อมูลผลกระทบ'}</p></div></div></details>
      <section className="conversation"><div className="conversation-heading"><div><h3>บทสนทนา <span>{messages.length}</span></h3><span className={`chat-connection ${realtimeStatus === 'live' ? 'live' : 'waiting'}`} role="status"><i/>{realtimeStatus === 'live' ? 'เชื่อมต่อแล้ว · ข้อความเข้าทันที' : 'กำลังเชื่อมต่อข้อความใหม่…'}</span></div><button type="button" onClick={onRefreshMessages} disabled={messagesBusy} aria-label="โหลดข้อความใหม่" title="โหลดข้อความใหม่"><Icon name="history"/></button></div>
        <div ref={feedRef} className="conversation-feed" role="log" aria-label="บทสนทนาของคำขอ">{messagesBusy && messages.length === 0 ? <div className="chat-empty">กำลังโหลดข้อความ…</div> : messages.length === 0 ? <div className="chat-empty"><Icon name="message" size={32}/><b>เริ่มบทสนทนา</b><small>ส่งข้อความถึงเจ้าหน้าที่ที่ดูแล Ticket นี้ได้เลย</small></div> : messages.map(message => { const mine = message.author_id === currentUserId; const authorLabel = mine ? `คุณ · ${ROLE[message.author_role] || message.author_role}` : message.author_role === 'employee' ? 'พนักงาน' : message.author_role === 'admin' ? 'ผู้ดูแลระบบ' : `Operator · ${message.author_email.split('@')[0]}`; return <article key={message.id} className={`chat-message ${message.author_role === 'employee' ? 'from-employee' : 'from-agent'} ${mine ? 'mine' : 'theirs'}`}><div className="chat-author"><b>{authorLabel}</b><time>{new Date(message.created_at).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })}</time></div><p>{message.body}</p></article>; })}</div>
        {messagesError && <div className="chat-error" role="alert">{messagesError}</div>}
        <form className="chat-composer" onSubmit={onSendMessage}><textarea value={messageDraft} onChange={e => setMessageDraft(e.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} maxLength={4000} rows={1} placeholder={role === 'employee' ? 'พิมพ์ข้อความถึงเจ้าหน้าที่…' : 'พิมพ์ข้อความตอบพนักงาน…'} aria-label="ข้อความในคำขอ"/><div><span>{messageDraft.length}/4000 · Enter ส่ง · Shift+Enter ขึ้นบรรทัดใหม่</span><button className="primary" disabled={messagesBusy || !messageDraft.trim()}>{messagesBusy ? 'กำลังส่ง…' : 'ส่ง'} <Icon name="send" size={18}/></button></div></form>
      </section>
      <details className="timeline-section"><summary className="timeline-heading"><div><h3>ประวัติการดำเนินงาน</h3></div><span className="activity-count">{activities.length} กิจกรรม <Icon name="chevron" size={14}/></span></summary><ol className="timeline">{activities.map((item, index) => <li key={`${item.kind}-${ticket.id}-${item.created_at}-${index}`} className={index === 0 ? 'latest' : ''}><span className={`timeline-dot ${item.kind === 'priority' ? 'priority' : STATUS[item.to_status]?.tone || ''}`}/><div className="activity-body"><b>{item.kind === 'priority' ? `ปรับความเร่งด่วน: ${item.from_priority === 'Urgent' ? 'เร่งด่วน' : 'ปกติ'} → ${item.to_priority === 'Urgent' ? 'เร่งด่วน' : 'ปกติ'}` : item.from_status ? `เปลี่ยนสถานะ: ${STATUS[item.from_status]?.label || item.from_status} → ${STATUS[item.to_status]?.label || item.to_status}` : `สร้างคำขอ · ${STATUS[item.to_status]?.label || item.to_status}`}</b><small>{item.actor_email || `ผู้ใช้ #${item.actor_id}`} <span>·</span> {new Date(item.created_at).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })}</small></div></li>)}</ol></details>
    </div>
    <div className="detail-bottom"><div className="detail-bottom-note"><Icon name="clock" size={18}/> เปิดมา {ageText(ticket.created_at, Date.now())}</div>{canUpdate ? <button className="primary" disabled={busy} onClick={() => onRequestStatusChange(ticket)}>{ticket.status === 'Open' ? 'รับงาน · เริ่มดำเนินการ' : 'ทำเครื่องหมายว่าเสร็จแล้ว'} <Icon name="arrow"/></button> : ticket.status === 'Done' ? <span className="done-label"><Icon name="check" size={18}/> ปิดงานเรียบร้อย</span> : <span className="employee-status-note">รอเจ้าหน้าที่อัปเดตสถานะ</span>}</div>
  </>;
}

function ConfirmDialog({ confirmation, busy, onCancel, onConfirm }) {
  const ref = useRef(null);
  useModalFocus(ref, true, onCancel, busy);
  const isPriority = confirmation.type === 'priority';
  const isLogout = confirmation.type === 'logout';
  const isAssignment = confirmation.type === 'assignment';
  const ticket = confirmation.ticket;
  const nextStatus = ticket?.status === 'Open' ? 'In Progress' : 'Done';
  const nextLabel = STATUS[nextStatus]?.label || nextStatus;
  const ticketCode = ticket ? `TC-${String(ticket.id).padStart(4, '0')}` : '';
  return <div className="modal-backdrop confirm-backdrop" onMouseDown={event => event.target === event.currentTarget && !busy && onCancel()}>
    <section ref={ref} className="confirm-modal" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-description">
      <div className={`confirm-icon ${isLogout ? 'logout' : nextStatus === 'Done' ? 'complete' : 'status'}`}><Icon name={isLogout ? 'logout' : isPriority ? 'flag' : nextStatus === 'Done' ? 'check' : 'history'} size={28}/></div>
      <h2 id="confirm-title">{isPriority ? 'ยืนยันปรับความเร่งด่วน' : isAssignment ? 'ยืนยันมอบหมายผู้รับผิดชอบ' : isLogout ? 'ยืนยันออกจากระบบ' : nextStatus === 'Done' ? 'ยืนยันปิด Ticket' : 'ยืนยันรับงาน'}</h2>
      <p id="confirm-description">{isPriority ? `เปลี่ยน ${ticketCode} เป็น${confirmation.priority === 'Urgent' ? 'เร่งด่วน' : 'ปกติ'} หลังประเมินผลกระทบแล้วใช่ไหม?` : isAssignment ? `ต้องการ${confirmation.assignee_id ? `มอบหมายให้ ${confirmation.assignee_name} ดูแล` : 'ยกเลิกการมอบหมาย'} ${ticketCode} ใช่ไหม?` : isLogout ? 'ต้องการออกจากระบบ TicketCenter ใช่ไหม?' : nextStatus === 'Done' ? `ต้องการเปลี่ยน ${ticketCode} เป็น “${nextLabel}” ใช่ไหม?` : `ต้องการรับ ${ticketCode} และเปลี่ยนสถานะเป็น “${nextLabel}” ใช่ไหม?`}</p>
      {!isLogout && <div className="confirm-ticket"><b>{ticket.title}</b><span>{ticketCode} · {ticket.department} · {isPriority ? 'ปรับลำดับความสำคัญของงาน' : isAssignment ? 'เปลี่ยนผู้รับผิดชอบ' : `${STATUS[ticket.status]?.label} → ${nextLabel}`}</span></div>}
      <div className="confirm-actions"><button className="secondary-button" onClick={onCancel} disabled={busy}>ยกเลิก</button><button className={`primary confirm-primary ${!isLogout && nextStatus === 'Done' ? 'danger' : ''}`} onClick={onConfirm} disabled={busy}>{busy ? 'กำลังดำเนินการ…' : isPriority ? 'ยืนยันปรับระดับ' : isAssignment ? 'ยืนยันมอบหมาย' : isLogout ? 'ออกจากระบบ' : nextStatus === 'Done' ? 'ยืนยันปิดงาน' : 'ยืนยันรับงาน'}</button></div>
    </section>
  </div>;
}

function useModalFocus(ref, open, onClose, busy) {
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement;
    const box = ref.current;
    box?.querySelector('button:not(:disabled),input:not(:disabled),select,textarea')?.focus();
    const keydown = event => {
      if (event.key === 'Escape' && !busy) { event.preventDefault(); closeRef.current(); }
      if (event.key !== 'Tab') return;
      const items = [...box.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled)')];
      const first = items[0], last = items.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    box?.addEventListener('keydown', keydown);
    return () => { box?.removeEventListener('keydown', keydown); previous?.focus(); };
  }, [open, busy]);
}

createRoot(document.getElementById('root')).render(<App/>);
