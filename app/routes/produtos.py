"""Rotas REST de Produto: /api/produtos"""

from flask import Blueprint, g, jsonify, request

from app.exceptions import RecursoNaoEncontradoError
from app.models.produto import Produto, ProdutoRepository
from app.services.estoque_service import EstoqueService
from app.models.movimentacao import MovimentacaoRepository

produtos_bp = Blueprint("produtos", __name__, url_prefix="/api/produtos")


def _repo() -> ProdutoRepository:
    return ProdutoRepository(g.db)


def _estoque_service() -> EstoqueService:
    return EstoqueService(ProdutoRepository(g.db), MovimentacaoRepository(g.db))


@produtos_bp.post("")
def criar_produto():
    dados = request.get_json(silent=True) or {}
    campos_obrigatorios = {"nome", "preco", "categoria_id"}
    faltando = campos_obrigatorios - dados.keys()
    if faltando:
        return jsonify({"erro": f"campos obrigatórios ausentes: {sorted(faltando)}"}), 400

    produto = Produto(
        id=None,
        nome=dados["nome"],
        descricao=dados.get("descricao"),
        preco=float(dados["preco"]),
        quantidade=int(dados.get("quantidade", 0)),
        categoria_id=int(dados["categoria_id"]),
    )
    produto = _repo().criar(produto)
    return jsonify(produto.to_dict()), 201


@produtos_bp.get("")
def listar_produtos():
    categoria_id = request.args.get("categoria_id", type=int)
    produtos = _repo().listar(categoria_id=categoria_id)
    return jsonify([p.to_dict() for p in produtos])


@produtos_bp.get("/<int:produto_id>")
def buscar_produto(produto_id: int):
    try:
        produto = _repo().buscar_por_id(produto_id)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify(produto.to_dict())


@produtos_bp.put("/<int:produto_id>")
def atualizar_produto(produto_id: int):
    dados = request.get_json(silent=True) or {}
    try:
        produto = _repo().atualizar(produto_id, dados)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify(produto.to_dict())


@produtos_bp.delete("/<int:produto_id>")
def excluir_produto(produto_id: int):
    try:
        _repo().excluir(produto_id)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return "", 204


@produtos_bp.get("/<int:produto_id>/movimentacoes")
def historico_produto(produto_id: int):
    try:
        movimentacoes = _estoque_service().historico_do_produto(produto_id)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify([m.to_dict() for m in movimentacoes])
