import pytest
from app import app, db, DeploymentHistory, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('testpass')
            test_user = User(username='testadmin', password_hash=hashed_pw)
            db.session.add(test_user)
            db.session.commit()
            yield client
        with app.app_context():
            db.drop_all()

def test_login_redirect(client):
    # Unauthenticated user visiting root is redirected to login
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_successful_login(client):
    # Test JSON login payload
    response = client.post('/login', json={'username': 'testadmin', 'password': 'testpass'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] == True

def test_trigger_api_protected(client):
    # Post without auth returns 302 Redirect to login
    response = client.post('/api/trigger')
    assert response.status_code == 302

    # Login via json
    client.post('/login', json={'username': 'testadmin', 'password': 'testpass'})
    response = client.post('/api/trigger')
    assert response.status_code == 200
    assert response.get_json()['success'] == True

def test_webhook_api(client):
    # Test unauthenticated webhook submission (GitHub)
    payload = {
        "head_commit": {
            "message": "Update README.md"
        }
    }
    response = client.post('/api/webhook', json=payload)
    assert response.status_code == 200
    assert response.get_json()['success'] == True
    
    with app.app_context():
        history = DeploymentHistory.query.first()
        assert "Update README.md" in history.status
