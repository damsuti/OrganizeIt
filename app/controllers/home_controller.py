from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.task_model import create_task, get_tasks_by_user, delete_task

home_bp = Blueprint('home', __name__)

@home_bp.before_request
def check_session():
    if 'user_id' not in session and request.endpoint != 'auth.auth_page':
        return redirect(url_for('auth.auth_page'))
    

@home_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('username') )

@home_bp.route('/api/tasks', methods=['GET'])
def list_tasks():
    user_id = session['user_id']
    tasks = get_tasks_by_user(user_id)
    return jsonify(tasks), 200

@home_bp.route('/api/tasks',methods=['POST'])
def add_task():
    data = request.get_json() or {}
    titulo = data.get('titulo','').strip()
    dia_semana = data.get('dia_semana')
    horario = data.get('horario')

    if not titulo or not dia_semana or not horario:
        return jsonify({"error": "Preencha todos os campos!"}), 400
    
    create_task(session['user_id'], titulo,dia_semana,horario)
    return jsonify({"success":"Tarefa registrada com sucesso!"}), 201

@home_bp.route('/api/tasks', methods=['DELETE'])
def remove_task():
    """Remove uma tarefa específica do usuário logado."""
    data = request.get_json() or {}
    titulo = data.get('titulo')
    dia_semana = data.get('dia_semana')
    horario = data.get('horario')

    # Validação dos dados recebidos
    if not titulo or not dia_semana or not horario:
        return jsonify({"error": "Dados insuficientes para a exclusão."}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuário não autenticado."}), 401

    # Executa a query de deleção no banco Postgres
    delete_task(user_id, titulo, dia_semana, horario)
    
    return jsonify({"success": "Tarefa excluída com sucesso!"}), 200

@home_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.auth_page'))