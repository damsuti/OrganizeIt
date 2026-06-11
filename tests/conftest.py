import pytest
import psycopg2
import os

# Puxa as variáveis de ambiente que definimos no docker-compose.test.yml
def get_test_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db_test'),
        database=os.getenv('POSTGRES_DB', 'agenda_test_db'),
        user=os.getenv('POSTGRES_USER', 'test_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'test_password'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    """Garante a limpeza e inicialização do banco antes e depois de toda a suíte de testes."""
    
    # ---- ANTES DOS TESTES (Setup) ----
    conn = get_test_db_connection()
    cur = conn.cursor()
    
    # Derruba as tabelas antigas caso o container tenha sido reaproveitado
    cur.execute("DROP TABLE IF EXISTS tarefas CASCADE;")
    cur.execute("DROP TABLE IF EXISTS usuarios CASCADE;")
    
    # Cria as tabelas do zero para os testes começarem limpos
    cur.execute('''
        CREATE TABLE usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    ''')
    cur.execute('''
        CREATE TABLE tarefas (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            titulo VARCHAR(100) NOT NULL,
            dia_semana VARCHAR(20) NOT NULL,
            horario VARCHAR(10) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

    # O pytest para aqui, executa todos os seus arquivos de teste (.py)
    yield 

    # ---- DEPOIS DOS TESTES (Teardown) ----
    conn = get_test_db_connection()
    cur = conn.cursor()
    
    # Limpa tudo, deixando o banco zerado após a execução
    cur.execute("DROP TABLE IF EXISTS tarefas CASCADE;")
    cur.execute("DROP TABLE IF EXISTS usuarios CASCADE;")
    conn.commit()
    
    cur.close()
    conn.close()