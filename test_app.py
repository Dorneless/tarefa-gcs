import os

import psycopg2
import pytest

from app import app
import app as my_app

# Banco de testes em PostgreSQL. Fora do Docker, sobe-se um Postgres
# descartavel (ver GUIA_DEVOPS.md). No CI, vem do service "postgres".
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://gcs_user:gcs_pass@localhost:5435/gcs_test",
)


# --- FIXTURE (Configuração do ambiente de testes) ---
@pytest.fixture
def client():
    # 1. Recria um schema limpo e isolado a cada teste
    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS lancamento")
    cur.execute("DROP TABLE IF EXISTS usuario")
    cur.execute(
        "CREATE TABLE usuario ("
        "id SERIAL PRIMARY KEY, nome TEXT, login TEXT, "
        "senha TEXT, situacao TEXT)"
    )
    cur.execute(
        "CREATE TABLE lancamento ("
        "id SERIAL PRIMARY KEY, descricao TEXT, data_lancamento DATE, "
        "valor NUMERIC(12, 2), tipo_lancamento TEXT, situacao TEXT)"
    )

    # 2. Insere um usuário e um lançamento de teste
    cur.execute(
        "INSERT INTO usuario (nome, login, senha, situacao) "
        "VALUES ('Admin', 'admin123', 'senhaSegura', 'Ativo')"
    )
    cur.execute(
        "INSERT INTO lancamento "
        "(descricao, data_lancamento, valor, tipo_lancamento, situacao) "
        "VALUES ('Luz', '2026-04-14', 100.0, 'Despesa', 'Pendente')"
    )
    cur.close()
    conn.close()

    app.config["TESTING"] = True
    # Bloqueia o envio de e-mails reais durante os testes
    app.config["MAIL_SUPPRESS_SEND"] = True

    # 3. Força a aplicação a usar o banco temporário
    def override_get_db_connection():
        return psycopg2.connect(TEST_DATABASE_URL)

    my_app.get_db_connection = override_get_db_connection

    # 4. Entrega o cliente de testes
    with app.test_client() as test_client:
        yield test_client


# --- FUNÇÃO AUXILIAR ---
def realiza_login(client):
    return client.post(
        "/login",
        data={"login": "admin123", "senha": "senhaSegura"},
        follow_redirects=True,
    )


# --- OS 20 TESTES UNITÁRIOS ---


def test_01_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_02_login_success(client):
    response = realiza_login(client)
    assert b"Sair do Sistema" in response.data


def test_03_login_failure(client):
    response = client.post(
        "/login",
        data={"login": "errado", "senha": "123"},
        follow_redirects=True,
    )
    assert b"inv\xc3\xa1lidos" in response.data


def test_04_logout(client):
    realiza_login(client)
    response = client.get("/logout", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_05_index_bloqueado_sem_login(client):
    response = client.get("/", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_06_index_carrega_com_login(client):
    realiza_login(client)
    response = client.get("/")
    assert response.status_code == 200


def test_07_listagem_exibe_lancamento_teste(client):
    realiza_login(client)
    response = client.get("/")
    assert b"Luz" in response.data


def test_08_create_bloqueado_sem_login(client):
    response = client.get("/create", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_09_create_page_loads(client):
    realiza_login(client)
    response = client.get("/create")
    assert response.status_code == 200


def test_10_create_lancamento_salva_no_banco(client):
    realiza_login(client)
    response = client.post(
        "/create",
        data={
            "descricao": "Venda de Bolo",
            "data_lancamento": "2026-05-01",
            "valor": "50.0",
            "tipo_lancamento": "Receita",
            "situacao": "Recebido",
        },
        follow_redirects=True,
    )
    assert b"Venda de Bolo" in response.data


def test_11_edit_bloqueado_sem_login(client):
    response = client.get("/edit/1", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_12_edit_page_loads(client):
    realiza_login(client)
    response = client.get("/edit/1")
    assert response.status_code == 200


def test_13_edit_lancamento_atualiza_dados(client):
    realiza_login(client)
    response = client.post(
        "/edit/1",
        data={
            "descricao": "Luz Editada",
            "data_lancamento": "2026-04-14",
            "valor": "120.0",
            "tipo_lancamento": "Despesa",
            "situacao": "Pago",
        },
        follow_redirects=True,
    )
    assert b"Luz Editada" in response.data


def test_14_delete_bloqueado_sem_login(client):
    response = client.post("/delete/1", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_15_delete_lancamento_remove_do_banco(client):
    realiza_login(client)
    response = client.post("/delete/1", follow_redirects=True)
    assert b"Luz" not in response.data


def test_16_filtro_por_data(client):
    realiza_login(client)
    response = client.get("/?data_filtro=2026-04-14")
    assert b"Luz" in response.data


def test_17_filtro_data_sem_resultados(client):
    realiza_login(client)
    response = client.get("/?data_filtro=2020-01-01")
    assert b"Luz" not in response.data


def test_18_filtro_por_situacao(client):
    realiza_login(client)
    response = client.get("/?situacao_filtro=Pendente")
    assert b"Luz" in response.data


def test_19_pdf_bloqueado_sem_login(client):
    response = client.get("/exportar_pdf", follow_redirects=True)
    assert b"Acesso ao Sistema" in response.data


def test_20_pdf_geracao_com_sucesso(client):
    realiza_login(client)
    response = client.get("/exportar_pdf")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
