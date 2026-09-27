import os
os.environ["DATABASE_URL"]="sqlite:///./test_pocketsmart.db"
os.environ["GEMINI_ENABLED"]="false"
os.environ["SECRET_KEY"]="test-secret"
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

# Initialize schema explicitly for direct TestClient calls.
from app.database import Base, engine
Base.metadata.create_all(bind=engine)

def auth():
    r=client.post('/register',json={'name':'Test User','email':'test@example.com','password':'password123'})
    if r.status_code==409:r=client.post('/login',json={'email':'test@example.com','password':'password123'})
    return r

def test_health():
    assert client.get('/health').status_code==200

def test_register_and_home():
    r=auth(); assert r.status_code==200 or r.status_code==201
    token=r.json()['access_token']
    payload={'budget':50000,'room_type':'Living Room','style':'modern','items':['lamp','rug'],'quantities':{},'notes':''}
    r=client.post('/generate-home',json=payload,headers={'Authorization':f'Bearer {token}'})
    assert r.status_code==200
    data=r.json(); assert data['source']=='fallback'; assert data['recommendations']

def test_party():
    r=auth(); token=r.json()['access_token']
    payload={'budget':80000,'guests':30,'event_type':'Birthday','venue':'home','city':'Chennai','food_preference':'mixed','notes':''}
    r=client.post('/generate-party',json=payload,headers={'Authorization':f'Bearer {token}'})
    assert r.status_code==200

def test_jewelry_multipart():
    r=auth(); token=r.json()['access_token']
    data={'budget':'25000','occasion':'Wedding','style':'Elegant','outfit_color':'green','metal_preference':'Gold','notes':''}
    r=client.post('/generate-jewelry',data=data,headers={'Authorization':f'Bearer {token}'})
    assert r.status_code==200

def test_history():
    r=auth(); token=r.json()['access_token']
    r=client.get('/history',headers={'Authorization':f'Bearer {token}'})
    assert r.status_code==200
