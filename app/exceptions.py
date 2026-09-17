"""Exceções de domínio da aplicação.

Ter exceções próprias (em vez de usar ValueError genérico em todo
lugar) é uma prática de Clean Code: deixa explícito qual regra de
negócio foi violada e permite que as rotas convertam cada uma em um
código HTTP apropriado.
"""


class RecursoNaoEncontradoError(Exception):
    """Levantada quando um recurso (categoria, produto, etc.) não existe."""


class CategoriaEmUsoError(Exception):
    """Levantada ao tentar excluir uma categoria que ainda tem produtos."""


class EstoqueInsuficienteError(Exception):
    """Levantada ao registrar uma saída maior que o estoque disponível."""


class DadosInvalidosError(Exception):
    """Levantada quando o payload recebido na API é inválido."""
