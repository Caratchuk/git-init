"""Camada de serviço: regras de negócio de estoque.

As rotas (Flask) não conversam diretamente com o banco — elas chamam
este serviço, que orquestra os repositórios. Isso mantém a lógica de
negócio (ex.: "não deixar o estoque ficar negativo") em um único lugar,
separada tanto do SQL quanto do HTTP.
"""

from app.exceptions import DadosInvalidosError, EstoqueInsuficienteError
from app.models.movimentacao import Movimentacao, MovimentacaoRepository
from app.models.produto import ProdutoRepository

TIPOS_VALIDOS = {"entrada", "saida"}


class EstoqueService:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
    ):
        self._produtos = produto_repository
        self._movimentacoes = movimentacao_repository

    def registrar_movimentacao(
        self, produto_id: int, tipo: str, quantidade: int
    ) -> Movimentacao:
        """Registra uma entrada ou saída e ajusta o saldo do produto.

        Levanta `DadosInvalidosError` para entradas malformadas e
        `EstoqueInsuficienteError` se uma saída for maior que o saldo
        disponível — a rota converte cada uma em um código HTTP.
        """
        if tipo not in TIPOS_VALIDOS:
            raise DadosInvalidosError(
                f"tipo deve ser um de {sorted(TIPOS_VALIDOS)}, recebido: {tipo!r}"
            )
        if quantidade <= 0:
            raise DadosInvalidosError("quantidade deve ser maior que zero")

        produto = self._produtos.buscar_por_id(produto_id)  # 404 se não existir

        if tipo == "entrada":
            nova_quantidade = produto.quantidade + quantidade
        else:  # saida
            if quantidade > produto.quantidade:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente: disponível {produto.quantidade}, "
                    f"solicitado {quantidade}"
                )
            nova_quantidade = produto.quantidade - quantidade

        movimentacao = self._movimentacoes.criar(
            Movimentacao(id=None, produto_id=produto_id, tipo=tipo, quantidade=quantidade)
        )
        self._produtos.atualizar_quantidade(produto_id, nova_quantidade)
        return movimentacao

    def historico_do_produto(self, produto_id: int) -> list[Movimentacao]:
        self._produtos.buscar_por_id(produto_id)  # garante 404 se não existir
        return self._movimentacoes.listar_por_produto(produto_id)
