import json

def test_registro_usuario(client):
    payload = {
        "username": "testuser",
        "password": "secretpassword123"
    }
    response = client.post('api/register',
                           data=json.dumps(payload),
                           content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 201
    assert "success" in data

def test_registro_usuario_duplicado(client):
    payload = {
        "username": "duplicateuser",
        "password": "password123"
    }

    client.post('/api/register', data=json.dumps(payload), content_type='application/json')
    response = client.post('api/register', data=json.dumps(payload), content_type='application/json')

    data = json.loads(response.data)
    assert response.status_code == 409
    assert "error" in data

def test_login_sucesso(client):
    """Cenário Feliz: Login com credenciais corretas deve retornar 200."""
    # 1. Cria o usuário primeiro
    payload = {
        "username": "loginuser",
        "password": "correctpassword"
    }
    client.post('/api/register', data=json.dumps(payload), content_type='application/json')
    
    # 2. Tenta logar
    response = client.post('/api/login', data=json.dumps(payload), content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert "success" in data

def test_login_senha_errada(client):
    """Cenário de Falha: Login com senha incorreta deve retornar 401."""
    # 1. Cria o usuário
    client.post('/api/register', 
                data=json.dumps({"username": "wrongpassuser", "password": "correctpassword"}), 
                content_type='application/json')
    
    # 2. Tenta logar com senha errada
    payload = {
        "username": "wrongpassuser",
        "password": "invalidpassword"
    }
    response = client.post('/api/login', data=json.dumps(payload), content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 401
    assert "error" in data