-- =====================================================================
-- V2__criar_tabela_categoria.sql  (Flyway)
-- Migration de demonstração: tabela EXCLUSIVA de Homologação.
-- NÃO é aplicada automaticamente (ambientes travados em FLYWAY_TARGET=1).
-- Aplicada SÓ em homologação via comando manual (ver Cenário B).
-- =====================================================================

CREATE TABLE categoria (
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    descricao  VARCHAR(255)
);

INSERT INTO categoria (nome, descricao) VALUES
('Moradia',     'Aluguel, contas de casa e condomínio'),
('Alimentação', 'Mercado, restaurantes e delivery'),
('Transporte',  'Combustível, transporte público e manutenção'),
('Lazer',       'Entretenimento, streaming e viagens');
