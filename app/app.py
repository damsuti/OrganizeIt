import os
import secrets
from flask import Flask
from dotenv import load_dotenv
from models.user_model import init_db
from models.task_model import init_task_db  # Importa a nova tabela
from controllers.auth_controller import auth_bp
from controllers.home_controller import home_bp  # Importa o novo controller

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)  # Registra as rotas do calendário

if __name__ == '__main__':
    init_db()
    init_task_db()
    # O host precisa ser 0.0.0.0 para aceitar conexões de fora do container!
    app.run(host='0.0.0.0', port=5000)