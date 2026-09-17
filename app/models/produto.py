"""Modelo e repositório de Produto."""

from dataclasses import dataclass
from sqlite3 import Connection

from app.exceptions import RecursoNaoEncontradoError


@dataclass
class Produto:
    id: int | None
    nome: str
    descricao: str | None
    preco: float
    quantidade: int
    categoria_id: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "categoria_id": self.categoria_id,
        }


class ProdutoRepository:
    """Encapsula todo o acesso SQL à tabela `produtos`."""

    def __init__(self, connection: Connection):
        self._conn = connection

    def criar(self, produto: Produto) -> Produto:
        cursor = self._conn.execute(
            """
            INSERT INTO produtos (nome, descricao, preco, quantidade, categoria_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                produto.nome,
                produto.descricao,
                produto.preco,
                produto.quantidade,
                produto.categoria_id,
            ),
        )
        self._conn.commit()
        produto.id = cursor.lastrowid
        return produto

    def listar(self, categoria_id: int | None = None) -> list[Produto]:
        if categoria_id is not None:
            linhas = self._conn.execute(
                """
                SELECT id, nome, descricao, preco, quantidade, categoria_id
                FROM produtos WHERE categoria_id = ? ORDER BY nome
                """,
                (categoria_id,),
            ).fetchall()
        else:
            linhas = self._conn.execute(
                """
                SELECT id, nome, descricao, preco, quantidade, categoria_id
                FROM produtos ORDER BY nome
                """
            ).fetchall()
        return [self._linha_para_produto(linha) for linha in linhas]

    def buscar_por_id(self, produto_id: int) -> Produto:
        linha = self._conn.execute(
            """
            SELECT id, nome, descricao, preco, quantidade, categoria_id
            FROM produtos WHERE id = ?
            """,
            (produto_id,),
        ).fetchone()
        if linha is None:
            raise RecursoNaoEncontradoError(f"Produto {produto_id} não encontrado")
        return self._linha_para_produto(linha)

    def atualizar(self, produto_id: int, dados: dict) -> Produto:
        produto_atual = self.buscar_por_id(produto_id)
        nome = dados.get("nome", produto_atual.nome)
        descricao = dados.get("descricao", produto_atual.descricao)
        preco = dados.get("preco", produto_atual.preco)
        categoria_id = dados.get("categoria_id", produto_atual.categoria_id)

        self._conn.execute(
            """
            UPDATE produtos
            SET nome = ?, descricao = ?, preco = ?, categoria_id = ?
            WHERE id = ?
            """,
            (nome, descricao, preco, categoria_id, produto_id),
        )
        self._conn.commit()
        return self.buscar_por_id(produto_id)

    def atualizar_quantidade(self, produto_id: int, nova_quantidade: int) -> None:
        """Usado pela camada de serviço ao registrar uma movimentação."""
        self._conn.execute(
            "UPDATE produtos SET quantidade = ? WHERE id = ?",
            (nova_quantidade, produto_id),
        )
        self._conn.commit()

    def excluir(self, produto_id: int) -> None:
        self.buscar_por_id(produto_id)
        self._conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self._conn.commit()

    @staticmethod
    def _linha_para_produto(linha) -> Produto:
        return Produto(
            id=linha["id"],
            nome=linha["nome"],
            descricao=linha["descricao"],
            preco=linha["preco"],
            quantidade=linha["quantidade"],
            categoria_id=linha["categoria_id"],
        )
