from tests.base import ApiTestCase


class TestProdutos(ApiTestCase):
    def test_criar_e_buscar_produto(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, nome="Teclado")

        resposta = self.client.get(f"/api/produtos/{produto_id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["nome"], "Teclado")
        self.assertEqual(resposta.get_json()["categoria_id"], categoria_id)

    def test_criar_produto_sem_campos_obrigatorios_retorna_400(self):
        resposta = self.client.post("/api/produtos", json={"nome": "Sem categoria"})
        self.assertEqual(resposta.status_code, 400)

    def test_listar_produtos_filtrando_por_categoria(self):
        categoria_a = self.criar_categoria(nome="A")
        categoria_b = self.criar_categoria(nome="B")
        self.criar_produto(categoria_a, nome="Produto A1")
        self.criar_produto(categoria_b, nome="Produto B1")

        resposta = self.client.get(f"/api/produtos?categoria_id={categoria_a}")
        produtos = resposta.get_json()
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos[0]["nome"], "Produto A1")

    def test_atualizar_produto(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id, preco=10.0)

        resposta = self.client.put(
            f"/api/produtos/{produto_id}", json={"preco": 25.5}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["preco"], 25.5)

    def test_excluir_produto(self):
        categoria_id = self.criar_categoria()
        produto_id = self.criar_produto(categoria_id)

        resposta = self.client.delete(f"/api/produtos/{produto_id}")
        self.assertEqual(resposta.status_code, 204)

        resposta = self.client.get(f"/api/produtos/{produto_id}")
        self.assertEqual(resposta.status_code, 404)
