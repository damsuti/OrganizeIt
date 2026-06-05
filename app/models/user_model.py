import os
import psycopg2
from werkzeug.security import generate_password_hash

def get_db_connection():
    # Coleta as credenciais básicas do ambiente
    user = os.getenv('POSTGRES_USER', 'admin_agenda')
    password = os.getenv('POSTGRES_PASSWORD', 'senha_secreta_infra')
    database = os.getenv('POSTGRES_DB', 'agenda_db')
    port = os.getenv('POSTGRES_PORT', '5432')
    
    # Se estiver no Docker, lerá 'db' do compose. Se estiver local, assume '127.0.0.1'
    host_final = os.getenv('POSTGRES_HOST', '127.0.0.1')
    
    return psycopg2.connect(
        user=user,
        password=password,
        database=database,
        host=host_final,
        port=port
    )

def init_db():
    """Garante que a tabela de usuários exista na subida do container."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def create_user(username, password):
    """Insere um novo usuário com a senha criptografada."""
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cur.execute(
            'INSERT INTO usuarios (username, password_hash) VALUES (%s, %s) RETURNING id;',
            (username, hashed_password)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError:
        conn.rollback()
        return None  # Usuário já existe
    finally:
        cur.close()
        conn.close()

def get_user_by_username(username):
    """Busca um usuário pelo username."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, password_hash FROM usuarios WHERE username = %s;', (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "password_hash": user[2]}
    return None