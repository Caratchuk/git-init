from tests.base import ApiTestCase


class TestCategorias(ApiTestCase):
    def test_criar_e_listar_categoria(self):
        resposta = self.client.post("/api/categorias", json={"nome": "Livros"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.get_json()["nome"], "Livros")

        resposta = self.client.get("/api/categorias")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.get_json()), 1)

    def test_criar_categoria_sem_nome_retorna_400(self):
        resposta = self.client.post("/api/categorias", json={})
        self.assertEqual(resposta.status_code, 400)

    def test_buscar_categoria_inexistente_retorna_404(self):
        resposta = self.client.get("/api/categorias/999")
        self.assertEqual(resposta.status_code, 404)

    def test_atualizar_categoria(self):
        categoria_id = self.criar_categoria(nome="Antigo Nome")
        resposta = self.client.put(
            f"/api/categorias/{categoria_id}", json={"nome": "Novo Nome"}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["nome"], "Novo Nome")

    def test_excluir_categoria_com_produto_retorna_409(self):
        categoria_id = self.criar_categoria()
        self.criar_produto(categoria_id)
        resposta = self.client.delete(f"/api/categorias/{categoria_id}")
        self.assertEqual(resposta.status_code, 409)

    def test_excluir_categoria_sem_produtos(self):
        categoria_id = self.criar_categoria()
        resposta = self.client.delete(f"/api/categorias/{categoria_id}")
        self.assertEqual(resposta.status_code, 204)
