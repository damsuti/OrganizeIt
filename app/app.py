import os
from flask import Flask
from dotenv import load_dotenv
from models.user_model import init_db
from controllers.auth_controller import auth_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-default-mvc')

# Registra as rotas mapeadas pelo Controller
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    # Inicializa as tabelas de infraestrutura antes de abrir a porta do Flask
    init_db()
    app.run(host='0.0.0.0', port=5000)