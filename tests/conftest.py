import os
import sys
import pytest

# Injeta a pasta app diretamente no PATH do sistema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

# Agora importamos os módulos diretamente, sem o prefixo "app."
from app import app as flask_app
from models.user_model import get_db_connection

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
# ... (resto do arquivo continua igual)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()
    conn.close()

    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()