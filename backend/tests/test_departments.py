import pytest
from test_flow import client, auth
from app.realtime import event_visible

@pytest.mark.parametrize('department', ['FAC', 'FIN', 'PROC'])
def test_new_department_routing_permissions_assignment_and_conversation(client, department):
    admin = auth(client, 'admin@example.test')
    employee = auth(client, 'employee@example.test')
    hr = auth(client, 'hr@example.test')
    email = department.lower()+'@example.test'
    result = client.post('/api/admin/users', headers=admin, json={'display_name':'Service Agent','email':email,'password':'new-password-123','role':'agent','department':department,'is_active':True})
    assert result.status_code == 201
    user_id=result.json()['id']
    login = client.post('/api/login',json={'email':email,'password':'new-password-123'})
    assert login.status_code == 200
    agent={'Authorization':'Bearer '+login.json()['access_token']}
    ticket=client.post('/api/tickets',headers=employee,json={'title':'New department issue','description':'Please check the request','impact':'One team needs help','category':department,'department':'IT'}).json()
    assert ticket['department']==department and ticket['priority']=='Normal'
    path=f"/api/tickets/{ticket['id']}"
    assert client.get(path,headers=hr).status_code==404
    assert client.get(path+'/messages',headers=hr).status_code==404
    assert client.patch(path+'/priority',headers=hr,json={'priority':'Urgent'}).status_code==404
    assert client.patch(path+'/priority',headers=agent,json={'priority':'Urgent'}).status_code==200
    assert client.patch(f"/api/admin/tickets/{ticket['id']}/assignee",headers=admin,json={'assignee_id':user_id}).status_code==200
    assert client.post(path+'/messages',headers=agent,json={'body':'We are handling your request'}).status_code==201
    assert len(client.get(path+'/messages',headers=employee).json())==1
    for status in ['In Progress','Done']:
        assert client.patch(path+'/status',headers=agent,json={'status':status}).status_code==200
    assert client.get(path,headers=employee).json()['status']=='Done'
    assert client.get('/api/dashboard',headers=agent).json()['by_department'][department]==1
    overview=client.get('/api/admin/overview',headers=admin).json()
    assert len(overview['by_department'])==5

def test_all_categories_and_department_validation(client):
    assert [c['category'] for c in client.get('/api/catalog').json()]==['IT','HR','FAC','FIN','PROC']
    admin=auth(client,'admin@example.test')
    assert client.post('/api/admin/users',headers=admin,json={'display_name':'Invalid Agent','email':'bad-dept@example.test','password':'new-password-123','role':'agent','department':'UNKNOWN','is_active':True}).status_code==422
    assert client.get('/api/events').status_code==401
    assert client.get('/api/events',headers=auth(client,'employee@example.test')).status_code==503

def test_realtime_metadata_never_crosses_ticket_permissions():
    event={'type':'message.created','ticket_id':10,'employee_id':1,'department':'FIN'}
    assert event_visible(event,{'id':1,'role':'employee','department':None})
    assert not event_visible(event,{'id':2,'role':'employee','department':None})
    for dept in ['IT','HR','FAC','PROC']:
        assert not event_visible(event,{'id':3,'role':'agent','department':dept})
    assert event_visible(event,{'id':4,'role':'agent','department':'FIN'})
    assert event_visible(event,{'id':5,'role':'admin','department':None})
