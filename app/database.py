"""
Camada de acesso ao banco de dados (SQLite).

Centraliza a conexão e a criação do esquema relacional, para que o
restante da aplicação nunca precise saber o caminho do arquivo do
banco nem repetir DDL (Data Definition Language).
"""

import sqlite3
from pathlib import Path


# Caminho do arquivo SQLite. Pode ser sobrescrito por variável de ambiente
# para facilitar testes (":memory:") ou deploy em outro caminho.
import os

DATABASE_PATH = os.environ.get("ESTOQUE_DB_PATH", "estoque.db")


def get_connection() -> sqlite3.Connection:
    """Abre e retorna uma nova conexão SQLite.

    - `row_factory = sqlite3.Row` permite acessar colunas por nome
      (ex.: `linha["nome"]`) em vez de por índice, o que deixa o código
      dos repositórios mais legível.
    - `PRAGMA foreign_keys = ON` garante que as chaves estrangeiras
      (relacionamentos entre categorias, produtos e movimentações)
      sejam de fato validadas pelo SQLite.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL CHECK (preco >= 0),
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
        ON DELETE CASCADE
);
"""


def init_db(connection: sqlite3.Connection | None = None) -> None:
    """Cria as tabelas do esquema relacional, caso ainda não existam.

    Aceita uma conexão opcional para permitir reaproveitar a mesma
    conexão em testes com banco em memória.
    """
    own_connection = connection is None
    conn = connection or get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        if own_connection:
            conn.close()
