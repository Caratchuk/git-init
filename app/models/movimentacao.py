"""Modelo e repositório de Movimentação de estoque (entrada/saída)."""

from dataclasses import dataclass
from sqlite3 import Connection


@dataclass
class Movimentacao:
    id: int | None
    produto_id: int
    tipo: str  # "entrada" ou "saida"
    quantidade: int
    data: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "data": self.data,
        }


class MovimentacaoRepository:
    """Encapsula todo o acesso SQL à tabela `movimentacoes`."""

    def __init__(self, connection: Connection):
        self._conn = connection

    def criar(self, movimentacao: Movimentacao) -> Movimentacao:
        cursor = self._conn.execute(
            """
            INSERT INTO movimentacoes (produto_id, tipo, quantidade)
            VALUES (?, ?, ?)
            """,
            (movimentacao.produto_id, movimentacao.tipo, movimentacao.quantidade),
        )
        self._conn.commit()
        movimentacao.id = cursor.lastrowid
        linha = self._conn.execute(
            "SELECT data FROM movimentacoes WHERE id = ?", (movimentacao.id,)
        ).fetchone()
        movimentacao.data = linha["data"]
        return movimentacao

    def listar_por_produto(self, produto_id: int) -> list[Movimentacao]:
        linhas = self._conn.execute(
            """
            SELECT id, produto_id, tipo, quantidade, data
            FROM movimentacoes WHERE produto_id = ? ORDER BY data DESC
            """,
            (produto_id,),
        ).fetchall()
        return [self._linha_para_movimentacao(linha) for linha in linhas]

    def listar_todas(self) -> list[Movimentacao]:
        linhas = self._conn.execute(
            """
            SELECT id, produto_id, tipo, quantidade, data
            FROM movimentacoes ORDER BY data DESC
            """
        ).fetchall()
        return [self._linha_para_movimentacao(linha) for linha in linhas]

    @staticmethod
    def _linha_para_movimentacao(linha) -> Movimentacao:
        return Movimentacao(
            id=linha["id"],
            produto_id=linha["produto_id"],
            tipo=linha["tipo"],
            quantidade=linha["quantidade"],
            data=linha["data"],
        )
