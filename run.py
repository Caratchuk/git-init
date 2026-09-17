"""Ponto de entrada para rodar a aplicação localmente.

    python run.py

A API sobe em http://localhost:5000
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
