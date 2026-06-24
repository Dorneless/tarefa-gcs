-- =====================================================================
-- V1__init.sql  (Flyway - migration base / baseline)
-- Cria o schema inicial e popula os dados de exemplo do projeto.
-- Aplicada automaticamente em Homologação E Produção.
-- =====================================================================

CREATE TABLE usuario (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100),
    login     VARCHAR(100),
    senha     VARCHAR(100),
    situacao  VARCHAR(20)
);

CREATE TABLE lancamento (
    id               SERIAL PRIMARY KEY,
    descricao        VARCHAR(255),
    data_lancamento  DATE,
    valor            NUMERIC(12, 2),
    tipo_lancamento  VARCHAR(20),
    situacao         VARCHAR(20)
);

-- Usuário base (mesmas credenciais usadas no login)
INSERT INTO usuario (nome, login, senha, situacao)
VALUES ('Admin', 'admin123', 'senhaSegura', 'Ativo');

-- Lançamentos base
INSERT INTO lancamento (descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES
('Conta de Luz',             '2026-03-20', 150.50, 'Despesa', 'Pago'),
('Salário',                  '2026-03-05', 4500.00, 'Receita', 'Recebido'),
('Internet',                 '2026-03-15', 99.90,  'Despesa', 'Pago'),
('Supermercado',             '2026-03-10', 400.00, 'Despesa', 'Pago'),
('Venda de Bicicleta',       '2026-03-12', 800.00, 'Receita', 'Recebido'),
('Gasolina',                 '2026-03-18', 200.00, 'Despesa', 'Pendente'),
('Mensalidade Faculdade',    '2026-03-08', 600.00, 'Despesa', 'Pago'),
('Rendimento Investimento',  '2026-03-25', 150.00, 'Receita', 'Pendente'),
('Farmácia',                 '2026-03-22', 85.00,  'Despesa', 'Pago'),
('Freelance Design',         '2026-03-26', 300.00, 'Receita', 'Recebido');
