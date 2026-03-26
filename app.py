from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
# A chave secreta é obrigatória para usar o recurso de login (session) do Flask
app.secret_key = 'chave_super_secreta_gcs'

def get_db_connection():
    conn = sqlite3.connect('banco.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROTA DE LOGIN ---
@app.route('/login', methods=('GET', 'POST'))
def login():
    erro = None
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuario WHERE login = ? AND senha = ?', (login, senha)).fetchone()
        conn.close()

        if usuario is None:
            erro = 'Usuário ou senha inválidos. Tente novamente.'
        else:
            session['usuario_logado'] = usuario['nome']
            return redirect(url_for('index'))
            
    return render_template('login.html', erro=erro)

# --- ROTA DE LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login'))

# --- ROTAS DO CRUD (Protegidas) ---

@app.route('/')
def index():
    # Se não estiver logado, manda pro login
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    lancamentos = conn.execute('SELECT * FROM lancamento').fetchall()
    conn.close()
    return render_template('index.html', lancamentos=lancamentos, nome_usuario=session['usuario_logado'])

@app.route('/create', methods=('GET', 'POST'))
def create():
    if 'usuario_logado' not in session: return redirect(url_for('login'))

    if request.method == 'POST':
        descricao = request.form['descricao']
        data_lancamento = request.form['data_lancamento']
        valor = request.form['valor']
        tipo_lancamento = request.form['tipo_lancamento']
        situacao = request.form['situacao']

        conn = get_db_connection()
        conn.execute('INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES (?, ?, ?, ?, ?)',
                     (descricao, data_lancamento, valor, tipo_lancamento, situacao))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    if 'usuario_logado' not in session: return redirect(url_for('login'))

    conn = get_db_connection()
    lancamento = conn.execute('SELECT * FROM lancamento WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        descricao = request.form['descricao']
        data_lancamento = request.form['data_lancamento']
        valor = request.form['valor']
        tipo_lancamento = request.form['tipo_lancamento']
        situacao = request.form['situacao']

        conn.execute('UPDATE lancamento SET descricao = ?, data_lancamento = ?, valor = ?, tipo_lancamento = ?, situacao = ? WHERE id = ?',
                     (descricao, data_lancamento, valor, tipo_lancamento, situacao, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', lancamento=lancamento)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    if 'usuario_logado' not in session: return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM lancamento WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)