import sqlite3

# Conecta ao banco (ele será criado automaticamente na pasta)
conexao = sqlite3.connect('banco.sqlite')
cursor = conexao.cursor()

# Criação da tabela usuário [cite: 7]
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    login TEXT,
    senha TEXT,
    situacao TEXT
)
''')

# Criação da tabela lançamento [cite: 7]
cursor.execute('''
CREATE TABLE IF NOT EXISTS lancamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    data_lancamento TEXT,
    valor REAL,
    tipo_lancamento TEXT,
    situacao TEXT
)
''')

# Inserindo 1 usuário 
cursor.execute("INSERT INTO usuario (nome, login, senha, situacao) VALUES ('Admin', 'admin123', 'senhaSegura', 'Ativo')")

# Inserindo 10 lançamentos 
lancamentos = [
    ('Conta de Luz', '2026-03-20', 150.50, 'Despesa', 'Pago'),
    ('Salário', '2026-03-05', 4500.00, 'Receita', 'Recebido'),
    ('Internet', '2026-03-15', 99.90, 'Despesa', 'Pago'),
    ('Supermercado', '2026-03-10', 400.00, 'Despesa', 'Pago'),
    ('Venda de Bicicleta', '2026-03-12', 800.00, 'Receita', 'Recebido'),
    ('Gasolina', '2026-03-18', 200.00, 'Despesa', 'Pendente'),
    ('Mensalidade Faculdade', '2026-03-08', 600.00, 'Despesa', 'Pago'),
    ('Rendimento Investimento', '2026-03-25', 150.00, 'Receita', 'Pendente'),
    ('Farmácia', '2026-03-22', 85.00, 'Despesa', 'Pago'),
    ('Freelance Design', '2026-03-26', 300.00, 'Receita', 'Recebido')
]
cursor.executemany("INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES (?, ?, ?, ?, ?)", lancamentos)

conexao.commit()
conexao.close()
print("Banco de dados criado e populado com sucesso!")