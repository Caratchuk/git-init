"""Rotas REST de Movimentação de estoque: /api/movimentacoes"""

from flask import Blueprint, g, jsonify, request

from app.exceptions import (
    DadosInvalidosError,
    EstoqueInsuficienteError,
    RecursoNaoEncontradoError,
)
from app.models.movimentacao import MovimentacaoRepository
from app.models.produto import ProdutoRepository
from app.services.estoque_service import EstoqueService

movimentacoes_bp = Blueprint(
    "movimentacoes", __name__, url_prefix="/api/movimentacoes"
)


def _service() -> EstoqueService:
    return EstoqueService(ProdutoRepository(g.db), MovimentacaoRepository(g.db))


@movimentacoes_bp.post("")
def registrar_movimentacao():
    dados = request.get_json(silent=True) or {}
    campos_obrigatorios = {"produto_id", "tipo", "quantidade"}
    faltando = campos_obrigatorios - dados.keys()
    if faltando:
        return jsonify({"erro": f"campos obrigatórios ausentes: {sorted(faltando)}"}), 400

    try:
        movimentacao = _service().registrar_movimentacao(
            produto_id=int(dados["produto_id"]),
            tipo=str(dados["tipo"]),
            quantidade=int(dados["quantidade"]),
        )
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    except DadosInvalidosError as exc:
        return jsonify({"erro": str(exc)}), 400
    except EstoqueInsuficienteError as exc:
        return jsonify({"erro": str(exc)}), 409

    return jsonify(movimentacao.to_dict()), 201


@movimentacoes_bp.get("")
def listar_movimentacoes():
    movimentacoes = MovimentacaoRepository(g.db).listar_todas()
    return jsonify([m.to_dict() for m in movimentacoes])
