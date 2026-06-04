from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import check_password_hash
from models.user_model import create_user, get_user_by_username

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def auth_page():
    """Renderiza a View principal de autenticação."""
    return render_template('auth.html')

@auth_bp.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Preencha todos os campos!"}), 400

    user_id = create_user(username, password)
    if not user_id:
        return jsonify({"error": "Este nome de usuário já está em uso."}), 409

    return jsonify({"success": "Conta criada com sucesso! Faça o login."}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    user = get_user_by_username(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Usuário ou senha incorretos."}), 401

    # Cria a sessão do usuário na infraestrutura do Flask
    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({"success": "Login efetuado! Redirecionando...", "redirect": "/dashboard"}), 200 