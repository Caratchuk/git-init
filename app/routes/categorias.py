"""Rotas REST de Categoria: /api/categorias"""

from flask import Blueprint, g, jsonify, request

from app.exceptions import CategoriaEmUsoError, RecursoNaoEncontradoError
from app.models.categoria import CategoriaRepository

categorias_bp = Blueprint("categorias", __name__, url_prefix="/api/categorias")


def _repo() -> CategoriaRepository:
    return CategoriaRepository(g.db)


@categorias_bp.post("")
def criar_categoria():
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "campo 'nome' é obrigatório"}), 400

    categoria = _repo().criar(nome)
    return jsonify(categoria.to_dict()), 201


@categorias_bp.get("")
def listar_categorias():
    categorias = _repo().listar()
    return jsonify([c.to_dict() for c in categorias])


@categorias_bp.get("/<int:categoria_id>")
def buscar_categoria(categoria_id: int):
    try:
        categoria = _repo().buscar_por_id(categoria_id)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify(categoria.to_dict())


@categorias_bp.put("/<int:categoria_id>")
def atualizar_categoria(categoria_id: int):
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "campo 'nome' é obrigatório"}), 400

    try:
        categoria = _repo().atualizar(categoria_id, nome)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    return jsonify(categoria.to_dict())


@categorias_bp.delete("/<int:categoria_id>")
def excluir_categoria(categoria_id: int):
    try:
        _repo().excluir(categoria_id)
    except RecursoNaoEncontradoError as exc:
        return jsonify({"erro": str(exc)}), 404
    except CategoriaEmUsoError as exc:
        return jsonify({"erro": str(exc)}), 409
    return "", 204
