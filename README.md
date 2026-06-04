# OrganizeIT 🚀

O **OrganizeIT** é um ecossistema de gerenciamento de tarefas estruturado no padrão **MVC (Model-View-Controller)** utilizando Python com Flask no ecossistema Docker. O projeto conta com persistência robusta em PostgreSQL e uma suíte de testes de integração automatizados com Pytest.

---

## 🛠️ Tecnologias e Infraestrutura

* **Backend:** Python 3.12 & Flask 3.1
* **Banco de Dados:** PostgreSQL 15 (Isolado via Docker Containers)
* **Frontend:** HTML5, CSS3 (Bootstrap 5) & JavaScript Assíncrono (`fetch`)
* **Testes Automatizados:** Pytest 9
* **Orquestração de Ambiente:** Docker & Docker Compose

---

## 🚀 Como Executar o Projeto

Para rodar a aplicação localmente utilizando a infraestrutura conteinerizada, siga os passos abaixo:

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina física:
* Docker & Docker Compose
* Python 3.12+ (com ambiente virtual `venv` configurado)

### 2. Configurar as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as credenciais da infraestrutura (baseie-se no arquivo `.env.example`):

```ini
POSTGRES_USER=admin_agenda
POSTGRES_PASSWORD=senha_secreta_infra
POSTGRES_DB=agenda_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=chave-secreta-producao-swarm
```

### 3.Subir a Infraestrutura (Banco de Dados)
Para iniciar o banco de dados PostgreSQL estruturado com volume persistente e healthcheck ativo, execute o comando abaixo no terminal:
```
    docker-compose up -d
```

### 4.Iniciar a Aplicação Flask (Ambiente de Dev)
Com o banco ativo no Docker, inicialize o ambiente virtual do Python na raiz do projeto e execute o servidor:
```    # Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências se necessário
pip install -r app/requirements.txt

# Iniciar o servidor Flask mapeando o escopo
PYTHONPATH=. python3 app/app.py
```
Acesse a aplicação pelo seu navegador em: http://localhost:5000

### Como Executar os Testes Automatizados
A suíte de testes de integração do OrganizeIT valida o fluxo completo de autenticação (Registro, Duplicação de Contas, Login com Sucesso e Tratamento de Erros de Senha) direto no banco de dados de forma isolada.

Para rodar os testes, garanta que o container do banco de dados esteja de pé (docker-compose up -d) e execute o comando abaixo na raiz do projeto:
```
# Executa a suite completa em modo descritivo (verbose)
PYTHONPATH=. pytest -v
```