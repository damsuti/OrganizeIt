import os
import secrets
from flask import Flask
from dotenv import load_dotenv
from models.user_model import init_db
from models.task_model import init_task_db
from controllers.auth_controller import auth_bp
from controllers.home_controller import home_bp

load_dotenv()

# --- CORREÇÃO DE INFRAESTRUTURA PARA DOCKER ---
# Força o Flask a descobrir o caminho absoluto da pasta do script atual
base_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.join(base_dir, 'static')
template_dir = os.path.join(base_dir, 'templates')

# Inicializa o Flask amarrando as pastas de forma explícita para evitar o Erro 404
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
# ----------------------------------------------

app.secret_key = secrets.token_hex(32)

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)

if __name__ == '__main__':
    init_db()
    init_task_db()
    app.run(host='0.0.0.0', port=5000)