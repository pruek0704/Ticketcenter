from test_flow import client, auth

def create_ticket(client, headers, category="IT"):
    response = client.post('/api/tickets', headers=headers, json={"title": "Service request", "description": "Cannot use the service", "impact": "Work is blocked", "category": category})
    assert response.status_code == 201
    return response.json()

def account(role="employee", department=None, active=True):
    return {"display_name": "Test User", "role": role, "department": department, "is_active": active}

def test_admin_endpoints_require_admin_even_when_called_directly(client):
    for email in ('employee@example.test', 'it@example.test', 'hr@example.test'):
        headers = auth(client, email)
        for path in ('users', 'catalog', 'audit', 'overview'):
            assert client.get('/api/admin/' + path, headers=headers).status_code == 403
        assert client.post('/api/admin/users', headers=headers, json={**account(), "email": "new@example.test", "password": "new-password-123"}).status_code == 403
        assert client.put('/api/admin/users/1', headers=headers, json=account()).status_code == 403
        assert client.put('/api/admin/settings', headers=headers, json={"organization_name": "Org", "announcement": "", "accepting_tickets": False, "aging_hours": 24}).status_code == 403
        assert client.put('/api/admin/catalog/IT', headers=headers, json={"label": "IT", "description": "", "is_active": False}).status_code == 403
        assert client.post('/api/admin/users/1/reset-password', headers=headers, json={"password": "new-password-123"}).status_code == 403
        assert client.patch('/api/admin/tickets/1/assignee', headers=headers, json={"assignee_id": None}).status_code == 403
    assert client.get('/api/admin/users').status_code == 401

def test_account_creation_validation_login_and_no_secret_leak(client):
    admin = auth(client, 'admin@example.test')
    payload = {**account('agent', 'IT'), "email": "New.Agent@Example.test", "password": "new-password-123"}
    response = client.post('/api/admin/users', headers=admin, json=payload)
    assert response.status_code == 201
    assert response.json()['email'] == 'new.agent@example.test'
    assert 'password' not in response.text
    login = client.post('/api/login', json={"email": 'new.agent@example.test', "password": payload['password']})
    assert login.status_code == 200 and login.json()['user']['department'] == 'IT'
    assert client.post('/api/admin/users', headers=admin, json=payload).status_code == 409
    assert client.post('/api/admin/users', headers=admin, json={**payload, 'email': 'bad'}).status_code == 422
    assert client.post('/api/admin/users', headers=admin, json={**payload, 'email': 'agent2@example.test', 'department': None}).status_code == 422
    assert client.post('/api/admin/users', headers=admin, json={**payload, 'email': 'short@example.test', 'password': '123'}).status_code == 422
    audits = client.get('/api/admin/audit', headers=admin)
    assert 'new-password-123' not in audits.text and 'password_hash' not in audits.text
    assert audits.json()[0]['action'] == 'user.created'

def test_disabled_accounts_and_changed_permissions_revoke_existing_tokens(client):
    admin = auth(client, 'admin@example.test')
    it = auth(client, 'it@example.test')
    users = client.get('/api/admin/users', headers=admin).json()
    user_id = next(u['id'] for u in users if u['email'] == 'it@example.test')
    assert client.put(f'/api/admin/users/{user_id}', headers=admin, json=account('agent', 'HR')).status_code == 200
    assert client.get('/api/tickets', headers=it).status_code == 401
    hr_token = auth(client, 'it@example.test')
    assert client.put(f'/api/admin/users/{user_id}', headers=admin, json=account('agent', 'HR', False)).status_code == 200
    assert client.get('/api/me', headers=hr_token).status_code == 401
    assert client.post('/api/login', json={"email": "it@example.test", "password": "pass12345"}).status_code == 401

def test_settings_and_catalog_enforced_at_ticket_creation_without_hiding_old_work(client):
    admin = auth(client, 'admin@example.test')
    employee = auth(client, 'employee@example.test')
    it = auth(client, 'it@example.test')
    old_ticket = create_ticket(client, employee)
    settings = {"organization_name": "TicketCenter Demo Org", "announcement": "Maintenance window", "accepting_tickets": False, "aging_hours": 1}
    assert client.put('/api/admin/settings', headers=admin, json=settings).status_code == 200
    assert client.get('/api/settings', headers=employee).json() == settings
    assert client.get('/api/settings').status_code == 401
    assert client.get('/api/branding').json() == {'organization_name': settings['organization_name']}
    payload = {"title": "New issue", "description": "Details", "impact": "Work blocked", "category": "IT"}
    assert client.post('/api/tickets', headers=employee, json=payload).status_code == 409
    assert client.patch(f"/api/tickets/{old_ticket['id']}/status", headers=it, json={"status": "In Progress"}).status_code == 200
    assert client.put('/api/admin/settings', headers=admin, json={**settings, 'accepting_tickets': True}).status_code == 200
    assert client.put('/api/admin/catalog/IT', headers=admin, json={"label": "IT Helpdesk", "description": "Devices", "is_active": False}).status_code == 200
    assert [c['category'] for c in client.get('/api/catalog').json()] == ['HR', 'FAC', 'FIN', 'PROC']
    assert client.post('/api/tickets', headers=employee, json=payload).status_code == 409
    assert client.get(f"/api/tickets/{old_ticket['id']}", headers=employee).status_code == 200
    assert client.put('/api/admin/catalog/IT', headers=admin, json={"label": "IT Helpdesk", "description": "Devices", "is_active": True}).status_code == 200
    assert create_ticket(client, employee)['department'] == 'IT'
    assert client.put('/api/admin/settings', headers=admin, json={**settings, 'aging_hours': 0}).status_code == 422

def test_assignments_validate_department_and_preserve_queue_access(client):
    admin = auth(client, 'admin@example.test')
    employee = auth(client, 'employee@example.test')
    it = auth(client, 'it@example.test')
    hr = auth(client, 'hr@example.test')
    ticket = create_ticket(client, employee)
    users = client.get('/api/admin/users', headers=admin).json()
    it_id = next(u['id'] for u in users if u['email'] == 'it@example.test')
    hr_id = next(u['id'] for u in users if u['email'] == 'hr@example.test')
    path = f"/api/admin/tickets/{ticket['id']}/assignee"
    assert client.patch(path, headers=admin, json={'assignee_id': hr_id}).status_code == 422
    assert client.patch(path, headers=admin, json={'assignee_id': 999999}).status_code == 422
    assigned = client.patch(path, headers=admin, json={'assignee_id': it_id})
    assert assigned.status_code == 200 and assigned.json()['assignee_id'] == it_id
    assert assigned.json()['assignee_name'] == 'it@example.test'
    assert client.get(f"/api/tickets/{ticket['id']}", headers=hr).status_code == 404
    assert client.put(f'/api/admin/users/{it_id}', headers=admin, json=account('agent', 'IT', False)).status_code == 409
    assert client.patch(path, headers=admin, json={'assignee_id': None}).status_code == 200
    assert client.put(f'/api/admin/users/{it_id}', headers=admin, json=account('agent', 'IT', False)).status_code == 200
    assert client.patch(path, headers=admin, json={'assignee_id': it_id}).status_code == 422

def test_password_reset_revokes_tokens_and_is_audited_without_password(client):
    admin = auth(client, 'admin@example.test')
    employee = auth(client, 'employee@example.test')
    users = client.get('/api/admin/users', headers=admin).json()
    user_id = next(u['id'] for u in users if u['email'] == 'employee@example.test')
    assert client.post(f'/api/admin/users/{user_id}/reset-password', headers=admin, json={'password': 'changed-password-123'}).status_code == 200
    assert client.get('/api/me', headers=employee).status_code == 401
    assert client.post('/api/login', json={'email': 'employee@example.test', 'password': 'pass12345'}).status_code == 401
    assert client.post('/api/login', json={'email': 'employee@example.test', 'password': 'changed-password-123'}).status_code == 200
    result = client.get('/api/admin/audit', headers=admin)
    assert result.json()[0]['action'] == 'user.password_reset'
    assert 'changed-password-123' not in result.text

def test_admin_cannot_lock_out_own_account(client):
    admin = auth(client, 'admin@example.test')
    users = client.get('/api/admin/users', headers=admin).json()
    user_id = next(u['id'] for u in users if u['role'] == 'admin')
    assert client.put(f'/api/admin/users/{user_id}', headers=admin, json=account('employee')).status_code == 409
    assert client.put(f'/api/admin/users/{user_id}', headers=admin, json=account('admin', None, False)).status_code == 409
    assert client.post(f'/api/admin/users/{user_id}/reset-password', headers=admin, json={'password': 'new-password-123'}).status_code == 409
    assert client.get('/api/me', headers=admin).status_code == 200

def test_overview_counts_actual_work_and_department_totals(client):
    admin = auth(client, 'admin@example.test')
    employee = auth(client, 'employee@example.test')
    it = auth(client, 'it@example.test')
    ticket = create_ticket(client, employee)
    create_ticket(client, employee, 'HR')
    client.patch(f"/api/tickets/{ticket['id']}/priority", headers=it, json={'priority': 'Urgent'})
    overview = client.get('/api/admin/overview', headers=admin).json()
    assert (overview['total'], overview['open'], overview['urgent'], overview['unassigned']) == (2, 2, 1, 2)
    assert sum(d['total'] for d in overview['by_department']) == 2
    assert sum(d['count'] for d in overview['daily']) == 2
