from tests.base import ApiTestCase


class TestMovimentacoes(ApiTestCase):
    def test_entrada_aumenta_estoque(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, quantidade=5)

        resposta = self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 3},
        )
        self.assertEqual(resposta.status_code, 201)

        produto = self.client.get(f"/api/produtos/{produto_id}").get_json()
        self.assertEqual(produto["quantidade"], 8)

    def test_saida_diminui_estoque(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, quantidade=5)

        resposta = self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "saida", "quantidade": 2},
        )
        self.assertEqual(resposta.status_code, 201)

        produto = self.client.get(f"/api/produtos/{produto_id}").get_json()
        self.assertEqual(produto["quantidade"], 3)

    def test_saida_maior_que_estoque_retorna_409(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, quantidade=2)

        resposta = self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "saida", "quantidade": 10},
        )
        self.assertEqual(resposta.status_code, 409)

        # Estoque não deve ter sido alterado.
        produto = self.client.get(f"/api/produtos/{produto_id}").get_json()
        self.assertEqual(produto["quantidade"], 2)

    def test_tipo_invalido_retorna_400(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id)

        resposta = self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "transferencia", "quantidade": 1},
        )
        self.assertEqual(resposta.status_code, 400)

    def test_produto_inexistente_retorna_404(self):
        resposta = self.client.post(
            "/api/movimentacoes",
            json={"produto_id": 999, "tipo": "entrada", "quantidade": 1},
        )
        self.assertEqual(resposta.status_code, 404)

    def test_historico_do_produto(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, quantidade=5)

        self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "entrada", "quantidade": 3},
        )
        self.client.post(
            "/api/movimentacoes",
            json={"produto_id": produto_id, "tipo": "saida", "quantidade": 1},
        )

        resposta = self.client.get(f"/api/produtos/{produto_id}/movimentacoes")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.get_json()), 2)
