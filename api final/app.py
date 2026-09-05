"""
API do Kit Manager - banco de dados compartilhado
Schema baseado no Kits.py original (ID do time customizado, não autoincremento)

Rode localmente com: python app.py
Depois hospeda no Render pra ficar público
"""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os
from functools import wraps

app = Flask(__name__)

# Limita quantos pedidos cada IP pode fazer, pra impedir spam automatizado
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],  # limite geral pra qualquer rota
    storage_uri="memory://",
)

CAMINHO_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kits.db")

CHAVE_SECRETA = os.environ.get("API_KEY", "senha123")

COLUNAS = ['id', 'nome', 'camisa', 'calca', 'camisa_away', 'calca_away', 'camisa_gk', 'calca_gk']


def requer_chave(funcao):
    @wraps(funcao)
    def decorada(*args, **kwargs):
        chave_enviada = request.headers.get("X-API-KEY")
        if chave_enviada != CHAVE_SECRETA:
            return jsonify({"erro": "Chave de API inválida ou ausente"}), 401
        return funcao(*args, **kwargs)
    return decorada


def get_conexao():
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kits (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            camisa INTEGER,
            calca INTEGER,
            camisa_away INTEGER,
            calca_away INTEGER,
            camisa_gk INTEGER,
            calca_gk INTEGER
        )
    ''')
    conexao.commit()
    conexao.close()


# Roda na importação, pra funcionar tanto local quanto no Gunicorn (Render)
criar_tabela()


@app.route("/")
def home():
    return jsonify({"status": "API do Kit Manager rodando!"})


@app.route("/kits", methods=["GET"])
def listar_kits():
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM kits ORDER BY nome")
    resultados = cursor.fetchall()
    conexao.close()

    kits = [dict(linha) for linha in resultados]
    return jsonify(kits)


@app.route("/kits/<int:kit_id>", methods=["GET"])
def pegar_kit(kit_id):
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM kits WHERE id = ?", (kit_id,))
    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return jsonify({"erro": "Kit não encontrado"}), 404

    return jsonify(dict(resultado))


# Limite mais apertado nas rotas de escrita, já que são as que importam contra spam
@app.route("/kits/<int:kit_id>", methods=["PUT"])
@requer_chave
@limiter.limit("30 per minute")
def salvar_kit(kit_id):
    dados = request.get_json()

    conexao = get_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT id FROM kits WHERE id = ?", (kit_id,))
    ja_existe = cursor.fetchone() is not None

    cursor.execute('''
        INSERT INTO kits (id, nome, camisa, calca, camisa_away, calca_away, camisa_gk, calca_gk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            nome=excluded.nome,
            camisa=excluded.camisa,
            calca=excluded.calca,
            camisa_away=excluded.camisa_away,
            calca_away=excluded.calca_away,
            camisa_gk=excluded.camisa_gk,
            calca_gk=excluded.calca_gk
    ''', (
        kit_id,
        dados.get('nome'),
        dados.get('camisa'),
        dados.get('calca'),
        dados.get('camisa_away'),
        dados.get('calca_away'),
        dados.get('camisa_gk'),
        dados.get('calca_gk'),
    ))
    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Kit atualizado!" if ja_existe else "Kit cadastrado!",
        "ja_existia": ja_existe
    })


@app.route("/kits/<int:kit_id>", methods=["DELETE"])
@requer_chave
@limiter.limit("30 per minute")
def remover_kit(kit_id):
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM kits WHERE id = ?", (kit_id,))
    if cursor.fetchone() is None:
        conexao.close()
        return jsonify({"erro": "Kit não encontrado"}), 404

    cursor.execute("DELETE FROM kits WHERE id = ?", (kit_id,))
    conexao.commit()
    conexao.close()

    return jsonify({"mensagem": "Kit removido!"})


# Mensagem mais clara quando alguém estoura o limite, em vez do erro padrão
@app.errorhandler(429)
def limite_excedido(e):
    return jsonify({"erro": "Muitas requisições em pouco tempo. Espera um pouco e tenta de novo."}), 429


if __name__ == "__main__":
    modo_debug = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=modo_debug)