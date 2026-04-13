import pytest
from app import app, db, DeploymentHistory, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use memory DB for isolated tests
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test user
            hashed_pw = generate_password_hash('testpass')
            test_user = User(username='testadmin', password_hash=hashed_pw)
            db.session.add(test_user)
            db.session.commit()
            
            yield client
            
            db.session.remove()
            db.drop_all()

def test_login_redirect(client):
    # Unauthenticated user should be redirected to login
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_successful_login(client):
    response = client.post('/login', data={'username': 'testadmin', 'password': 'testpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Pipeline Overview' in response.data

def test_health_api_public(client):
    # Health API should remain public
    response = client.get('/api/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'

def test_trigger_api_protected(client):
    # Post without auth returns 302 Redirect to login
    response = client.post('/api/trigger')
    assert response.status_code == 302

    # Login and test
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})
    response = client.post('/api/trigger')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'
