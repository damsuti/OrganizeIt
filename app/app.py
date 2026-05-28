import os
import time
import logging
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Pega a pasta onde o app.py está e sobe um nível para achar o .env na raiz do projeto
path_env = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=path_env)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Recupera as variáveis originais do .env
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST_ENV = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')

# TRATAMENTO DE INFRA: Força 127.0.0.1 se o host lido for 'db' (indica execução local)
DB_HOST = '127.0.0.1' if DB_HOST_ENV == 'db' else DB_HOST_ENV

# LOG DE RECONHECIMENTO DE AMBIENTE
print("\n" + "="*50)
print(f" LOG DE INFRA - RECONHECIMENTO DE AMBIENTE:")
print(f" -> Arquivo .env carregado de: {path_env}")
print(f" -> Host original do .env: {DB_HOST_ENV}")
print(f" -> Host corrigido para execução local: {DB_HOST}:{DB_PORT}")
print(f" -> Usuário lido: {DB_USER}")
print(f" -> Banco lido: {DB_NAME}")
print("="*50 + "\n")

# Chave secreta necessária para gerenciar sessões/cookies de login de forma segura
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key-infra-dev')

def get_db_connection():
    """Tenta conectar ao banco de dados com uma estratégia simples de retry."""
    retries = 5
    while retries > 0:
        try:
            return psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                host=DB_HOST,
                port=DB_PORT
            )
        except psycopg2.OperationalError:
            logging.warning(f"Aguardando banco de dados... ({retries} tentativas restantes)")
            retries -= 1
            time.sleep(2)
    raise Exception("Database connection failed")

def init_db():
    """Cria as tabelas do sistema de tarefas se não existirem."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Tabela de Usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        );
    ''')
    
    # Tabela de Tarefas / Metas / Notas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            titulo VARCHAR(100) NOT NULL,
            descricao TEXT,
            tipo VARCHAR(20) NOT NULL, -- 'tarefa', 'meta', 'nota'
            data_alvo DATE NOT NULL,
            concluida BOOLEAN DEFAULT FALSE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Banco de dados de Tarefas inicializado com sucesso.")

# Inicializa o banco antes do Flask subir
init_db()

# --- ROTAS DE INFRAESTRUTURA ---
@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception:
        return jsonify({"status": "unhealthy"}), 500

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, password_hash FROM usuarios WHERE username = %s;', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        flash('Usuário ou senha incorretos!', 'danger')
        
    return """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <div class="container mt-5" style="max-width: 400px;">
        <h2 class="text-center mb-4">Agenda Infra - Login</h2>
        <form method="POST">
            <div class="mb-3"><input type="text" name="username" class="form-control" placeholder="Usuário" required></div>
            <div class="mb-3"><input type="password" name="password" class="form-control" placeholder="Senha" required></div>
            <button type="submit" class="btn btn-primary w-100">Entrar</button>
        </form>
        <p class="text-center mt-3"><a href="/register">Criar uma conta</a></p>
    </div>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO usuarios (username, password_hash) VALUES (%s, %s);', (username, hashed_password))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Este usuário já existe.', 'danger')
            
    return """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <div class="container mt-5" style="max-width: 400px;">
        <h2 class="text-center mb-4">Criar Conta</h2>
        <form method="POST">
            <div class="mb-3"><input type="text" name="username" class="form-control" placeholder="Novo Usuário" required></div>
            <div class="mb-3"><input type="password" name="password" class="form-control" placeholder="Senha" required></div>
            <button type="submit" class="btn btn-success w-100">Registrar</button>
        </form>
        <p class="text-center mt-3"><a href="/login">Voltar para o Login</a></p>
    </div>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTAS DA HOME / QUADRO DE TAREFAS ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo = request.form['tipo']
        data_alvo = request.form['data_alvo']
        
        cur.execute(
            'INSERT INTO tarefas (usuario_id, titulo, descricao, tipo, data_alvo) VALUES (%s, %s, %s, %s, %s);',
            (session['user_id'], titulo, descricao, tipo, data_alvo)
        )
        conn.commit()
    
    cur.execute('SELECT id, titulo, descricao, tipo, data_alvo, concluida FROM tarefas WHERE usuario_id = %s ORDER BY data_alvo ASC;', (session['user_id'],))
    tarefas = cur.fetchall()
    cur.close()
    conn.close()
    
    linhas_tarefas = ""
    for t in tarefas:
        badge_color = "primary" if t[3] == 'tarefa' else "success" if t[3] == 'meta' else "warning text-dark"
        linhas_tarefas += f"""
        <div class="card mb-2 shadow-sm">
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <span class="badge bg-{badge_color}">{t[3].upper()}</span>
                    <strong>{t[1]}</strong> - <small class="text-muted">{t[4]}</small>
                    <p class="mb-0 text-secondary" style="font-size: 0.9rem;">{t[2] or ''}</p>
                </div>
            </div>
        </div>
        """

    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Agenda de Metas e Tarefas (Olá, {session['username']}!)</h2>
            <a href="/logout" class="btn btn-outline-danger btn-sm">Sair</a>
        </div>
        
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card p-3 shadow-sm">
                    <h4>Novo Item</h4>
                    <form method="POST">
                        <div class="mb-2"><input type="text" name="titulo" class="form-control" placeholder="Título" required></div>
                        <div class="mb-2"><textarea name="descricao" class="form-control" placeholder="Descrição/Notas"></textarea></div>
                        <div class="mb-2">
                            <select name="tipo" class="form-select">
                                <option value="tarefa">Tarefa</option>
                                <option value="meta">Meta Diária</option>
                                <option value="nota">Nota</option>
                            </select>
                        </div>
                        <div class="mb-3"><input type="date" name="data_alvo" class="form-control" value="{datetime.now().strftime('%Y-%m-%d')}" required></div>
                        <button type="submit" class="btn btn-primary w-100">Adicionar à Agenda</button>
                    </form>
                </div>
            </div>
            
            <div class="col-md-8">
                <h4>Seus Afazeres e Metas Programadas</h4>
                {linhas_tarefas if tarefas else '<p class="text-muted">Nenhum item programado ainda. Comece adicionando um!</p>'}
            </div>
        </div>
    </div>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)