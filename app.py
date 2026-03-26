from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('banco.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Rota READ (Ler/Listar)
@app.route('/')
def index():
    conn = get_db_connection()
    lancamentos = conn.execute('SELECT * FROM lancamento').fetchall()
    conn.close()
    return render_template('index.html', lancamentos=lancamentos)

# Rota CREATE (Criar novo)
@app.route('/create', methods=('GET', 'POST'))
def create():
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

# Rota UPDATE (Editar)
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
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

# Rota DELETE (Excluir)
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM lancamento WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)