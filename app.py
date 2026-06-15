import os
from io import BytesIO

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Mail, Message
import psycopg2
import psycopg2.extras
from reportlab.pdfgen import canvas

# Carrega as variaveis definidas no arquivo .env para o ambiente
load_dotenv()

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURACAO SENSIVEL — lida exclusivamente de variaveis de ambiente.
# Nenhuma senha ou chave fica "chumbada" no codigo (ver .env / .env.example).
# -------------------------------------------------------------------------
app.secret_key = os.getenv("SECRET_KEY", "dev-fallback-trocar-em-producao")

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() in (
    "true",
    "1",
    "yes",
)
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)


def get_db_connection():
    """Abre uma conexao com o PostgreSQL usando a URL vinda do ambiente."""
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def dict_cursor(conn):
    """Cursor que devolve as linhas como dicionarios (lanc['descricao'])."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def notificar_por_email(descricao, valor):
    """Notifica por e-mail um novo lancamento.

    Em testes o envio e bloqueado por MAIL_SUPPRESS_SEND. Em producao,
    qualquer falha de SMTP e registrada mas NAO derruba o CRUD.
    """
    if not app.config.get("MAIL_USERNAME"):
        return
    try:
        msg = Message(
            subject="Novo lancamento registrado",
            recipients=[app.config["MAIL_USERNAME"]],
            body=f"O lancamento '{descricao}' (R$ {valor}) foi criado.",
        )
        mail.send(msg)
    except Exception:
        app.logger.exception("Falha ao enviar o e-mail de notificacao.")


# --- ROTA DE LOGIN ---
@app.route("/login", methods=("GET", "POST"))
def login():
    erro = None
    if request.method == "POST":
        login = request.form["login"]
        senha = request.form["senha"]

        conn = get_db_connection()
        cur = dict_cursor(conn)
        cur.execute(
            "SELECT * FROM usuario WHERE login = %s AND senha = %s",
            (login, senha),
        )
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if usuario is None:
            erro = "Usuário ou senha inválidos. Tente novamente."
        else:
            session["usuario_logado"] = usuario["nome"]
            return redirect(url_for("index"))

    return render_template("login.html", erro=erro)


# --- ROTA DE LOGOUT ---
@app.route("/logout")
def logout():
    session.pop("usuario_logado", None)
    return redirect(url_for("login"))


# --- ROTAS DO CRUD (Protegidas) ---


@app.route("/")
def index():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    data_filtro = request.args.get("data_filtro")
    situacao_filtro = request.args.get("situacao_filtro")

    query = "SELECT * FROM lancamento"
    clausulas = []
    params = []
    if data_filtro:
        clausulas.append("data_lancamento = %s")
        params.append(data_filtro)
    if situacao_filtro:
        clausulas.append("situacao = %s")
        params.append(situacao_filtro)
    if clausulas:
        query += " WHERE " + " AND ".join(clausulas)
    query += " ORDER BY id"

    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute(query, params)
    lancamentos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "index.html",
        lancamentos=lancamentos,
        nome_usuario=session["usuario_logado"],
        data_filtro=data_filtro or "",
        situacao_filtro=situacao_filtro or "",
    )


@app.route("/create", methods=("GET", "POST"))
def create():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        descricao = request.form["descricao"]
        data_lancamento = request.form["data_lancamento"]
        valor = request.form["valor"]
        tipo_lancamento = request.form["tipo_lancamento"]
        situacao = request.form["situacao"]

        conn = get_db_connection()
        cur = dict_cursor(conn)
        cur.execute(
            "INSERT INTO lancamento "
            "(descricao, data_lancamento, valor, tipo_lancamento, situacao) "
            "VALUES (%s, %s, %s, %s, %s)",
            (descricao, data_lancamento, valor, tipo_lancamento, situacao),
        )
        conn.commit()
        cur.close()
        conn.close()

        notificar_por_email(descricao, valor)
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/edit/<int:id>", methods=("GET", "POST"))
def edit(id):
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("SELECT * FROM lancamento WHERE id = %s", (id,))
    lancamento = cur.fetchone()

    if request.method == "POST":
        descricao = request.form["descricao"]
        data_lancamento = request.form["data_lancamento"]
        valor = request.form["valor"]
        tipo_lancamento = request.form["tipo_lancamento"]
        situacao = request.form["situacao"]

        cur.execute(
            "UPDATE lancamento SET descricao = %s, data_lancamento = %s, "
            "valor = %s, tipo_lancamento = %s, situacao = %s WHERE id = %s",
            (descricao, data_lancamento, valor, tipo_lancamento, situacao, id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.close()
    conn.close()
    return render_template("edit.html", lancamento=lancamento)


@app.route("/delete/<int:id>", methods=("POST",))
def delete(id):
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("DELETE FROM lancamento WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/exportar_pdf")
def exportar_pdf():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("SELECT * FROM lancamento ORDER BY id")
    lancamentos = cur.fetchall()
    cur.close()
    conn.close()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "Relatório de Lançamentos")
    pdf.setFont("Helvetica", 10)

    y = 760
    for lanc in lancamentos:
        linha = (
            f"#{lanc['id']} | {lanc['descricao']} | {lanc['data_lancamento']}"
            f" | R$ {lanc['valor']} | {lanc['tipo_lancamento']}"
            f" | {lanc['situacao']}"
        )
        pdf.drawString(50, y, linha)
        y -= 18
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 800

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    resposta = Response(buffer.read(), mimetype="application/pdf")
    resposta.headers["Content-Type"] = "application/pdf"
    resposta.headers["Content-Disposition"] = (
        "inline; filename=relatorio_lancamentos.pdf"
    )
    return resposta


if __name__ == "__main__":
    # Em producao quem serve a app e o gunicorn (ver Dockerfile).
    app.run(host="0.0.0.0", port=5000)
