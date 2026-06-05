import os
import psycopg2
from models.user_model import get_db_connection

def init_task_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                titulo VARCHAR(100) NOT NULL,
                dia_semana VARCHAR(20) NOT NULL,
                horario VARCHAR(10) NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE);
                ''')
    conn.commit()
    cur.close()
    conn.close()


def create_task(usuario_id, titulo, dia_semana, horario):
    """Insere uma nova tarefa para um usuário específico."""
    conn = get_db_connection()
    cur = conn.cursor()
    # CORREÇÃO: Passando os 4 parâmetros encapsulados dentro de uma tupla única
    cur.execute(
        'INSERT INTO tarefas (usuario_id, titulo, dia_semana, horario) VALUES (%s, %s, %s, %s) RETURNING id;',
        (usuario_id, titulo, dia_semana, horario)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return task_id

def get_tasks_by_user(usuario_id):
    """Busca todas as tarefas de um usuário específico."""
    conn = get_db_connection()
    cur = conn.cursor()
    # CORREÇÃO: Adicionada a vírgula para forçar o Python a criar uma tupla de 1 elemento
    cur.execute('SELECT titulo, dia_semana, horario FROM tarefas WHERE usuario_id = %s;', (usuario_id,))
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"titulo": t[0], "dia_semana": t[1], "horario": t[2]} for t in tasks]

def delete_task(usuario_id, titulo, dia_semana, horario):
    """Remove uma tarefa específica de um usuário no banco PostgreSQL."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        DELETE FROM tarefas 
        WHERE usuario_id = %s AND titulo = %s AND dia_semana = %s AND horario = %s;
    ''', (usuario_id, titulo, dia_semana, horario))
    conn.commit()
    cur.close()
    conn.close()

