"""Application factory.

Usar uma função `create_app` (em vez de um objeto Flask global) é uma
prática recomendada: permite criar instâncias diferentes da aplicação
para testes (com banco em memória) e para produção, sem que uma
configuração vaze para a outra.
"""

from flask import Flask, g, jsonify

from app.database import get_connection, init_db


def create_app(database_path: str | None = None) -> Flask:
    app = Flask(__name__)

    if database_path is not None:
        import app.database as database_module

        database_module.DATABASE_PATH = database_path

    with get_connection() as conn:
        init_db(conn)

    @app.before_request
    def abrir_conexao():
        g.db = get_connection()

    @app.teardown_request
    def fechar_conexao(exception=None):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    from app.routes.categorias import categorias_bp
    from app.routes.produtos import produtos_bp
    from app.routes.movimentacoes import movimentacoes_bp

    app.register_blueprint(categorias_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(movimentacoes_bp)

    return app
