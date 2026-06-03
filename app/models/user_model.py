import os
import psycopg2
from werkzeug.security import generate_password_hash

def get_db_connection():
    # Lê o host do arquivo .env
    host_env = os.getenv('POSTGRES_HOST')
    
    # Inteligência de Infra: Se for 'db', altera para 127.0.0.1 para conseguir rodar localmente
    host_final = '127.0.0.1' if host_env == 'db' else host_env
    
    return psycopg2.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        host=host_final,
        port=os.getenv('POSTGRES_PORT')
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