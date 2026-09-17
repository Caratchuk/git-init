"""Classe base para os testes: cria um banco SQLite temporário por teste."""

import os
import tempfile
import unittest

from app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(database_path=self._db_path)
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def criar_categoria(self, nome="Eletrônicos") -> int:
        resposta = self.client.post("/api/categorias", json={"nome": nome})
        return resposta.get_json()["id"]

    def criar_produto(self, categoria_id, **overrides) -> int:
        payload = {
            "nome": "Mouse sem fio",
            "descricao": "Mouse óptico USB",
            "preco": 59.9,
            "quantidade": 10,
            "categoria_id": categoria_id,
        }
        payload.update(overrides)
        resposta = self.client.post("/api/produtos", json=payload)
        return resposta.get_json()["id"]
