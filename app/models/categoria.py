"""Modelo e repositório de Categoria.

Cada "modelo" aqui é uma classe simples (dataclass) que representa uma
linha da tabela, e cada "repositório" é uma classe que sabe como ler e
escrever essas linhas no banco usando SQL parametrizado — nunca
concatenando strings, para evitar SQL Injection.
"""

from dataclasses import dataclass
from sqlite3 import Connection, IntegrityError

from app.exceptions import CategoriaEmUsoError, RecursoNaoEncontradoError


@dataclass
class Categoria:
    id: int | None
    nome: str

    def to_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome}


class CategoriaRepository:
    """Encapsula todo o acesso SQL à tabela `categorias`."""

    def __init__(self, connection: Connection):
        self._conn = connection

    def criar(self, nome: str) -> Categoria:
        cursor = self._conn.execute(
            "INSERT INTO categorias (nome) VALUES (?)", (nome,)
        )
        self._conn.commit()
        return Categoria(id=cursor.lastrowid, nome=nome)

    def listar(self) -> list[Categoria]:
        linhas = self._conn.execute(
            "SELECT id, nome FROM categorias ORDER BY nome"
        ).fetchall()
        return [Categoria(id=linha["id"], nome=linha["nome"]) for linha in linhas]

    def buscar_por_id(self, categoria_id: int) -> Categoria:
        linha = self._conn.execute(
            "SELECT id, nome FROM categorias WHERE id = ?", (categoria_id,)
        ).fetchone()
        if linha is None:
            raise RecursoNaoEncontradoError(f"Categoria {categoria_id} não encontrada")
        return Categoria(id=linha["id"], nome=linha["nome"])

    def atualizar(self, categoria_id: int, nome: str) -> Categoria:
        self.buscar_por_id(categoria_id)  # garante que existe (404 se não)
        self._conn.execute(
            "UPDATE categorias SET nome = ? WHERE id = ?", (nome, categoria_id)
        )
        self._conn.commit()
        return Categoria(id=categoria_id, nome=nome)

    def excluir(self, categoria_id: int) -> None:
        self.buscar_por_id(categoria_id)
        try:
            self._conn.execute(
                "DELETE FROM categorias WHERE id = ?", (categoria_id,)
            )
            self._conn.commit()
        except IntegrityError as exc:
            # A FOREIGN KEY em produtos.categoria_id bloqueia a exclusão
            # quando ainda existem produtos vinculados a essa categoria.
            raise CategoriaEmUsoError(
                "Não é possível excluir: existem produtos nesta categoria"
            ) from exc
