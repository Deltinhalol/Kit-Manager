"""
API do Kit Manager - banco de dados compartilhado
Rode localmente com: python app.py
Depois hospeda no Render/Railway pra ficar público
"""

from flask import Flask, request, jsonify
import sqlite3
import os
from functools import wraps

app = Flask(__name__)

CAMINHO_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kits.db")

# A chave secreta vem de uma variável de ambiente (mais seguro que deixar escrito no código)
# No Render, você configura isso em Settings > Environment
# Localmente, se não definir, usa "senha123" só pra testar
CHAVE_SECRETA = os.environ.get("API_KEY", "senha123")


def requer_chave(funcao):
    """Decorator que bloqueia a rota se não vier a chave certa no header"""
    @wraps(funcao)
    def decorada(*args, **kwargs):
        chave_enviada = request.headers.get("X-API-KEY")
        if chave_enviada != CHAVE_SECRETA:
            return jsonify({"erro": "Chave de API inválida ou ausente"}), 401
        return funcao(*args, **kwargs)
    return decorada


def get_conexao():
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conexao


def criar_tabela():
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            tipo TEXT NOT NULL,
            camisa_id TEXT NOT NULL,
            short_id TEXT NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()


@app.route("/")
def home():
    return jsonify({"status": "API do Kit Manager rodando!"})


# Lista todos os kits (ou filtra por time se passar ?time=Flamengo)
# LIVRE pra qualquer um ver, sem precisar de chave
@app.route("/kits", methods=["GET"])
def listar_kits():
    time_filtro = request.args.get("time")

    conexao = get_conexao()
    cursor = conexao.cursor()

    if time_filtro:
        cursor.execute("SELECT * FROM kits WHERE time = ?", (time_filtro,))
    else:
        cursor.execute("SELECT * FROM kits")

    resultados = cursor.fetchall()
    conexao.close()

    kits = [dict(linha) for linha in resultados]
    return jsonify(kits)


# Pega um kit específico pelo ID - também livre
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


# Adiciona um novo kit - PROTEGIDO, precisa da chave
@app.route("/kits", methods=["POST"])
@requer_chave
def adicionar_kit():
    dados = request.get_json()

    campos_obrigatorios = ["time", "tipo", "camisa_id", "short_id"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400

    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO kits (time, tipo, camisa_id, short_id) VALUES (?, ?, ?, ?)",
        (dados["time"], dados["tipo"], dados["camisa_id"], dados["short_id"])
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()

    return jsonify({"mensagem": "Kit adicionado!", "id": novo_id}), 201


# Edita um kit existente - PROTEGIDO, precisa da chave
@app.route("/kits/<int:kit_id>", methods=["PUT"])
@requer_chave
def editar_kit(kit_id):
    dados = request.get_json()

    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM kits WHERE id = ?", (kit_id,))
    if cursor.fetchone() is None:
        conexao.close()
        return jsonify({"erro": "Kit não encontrado"}), 404

    cursor.execute(
        """UPDATE kits SET time = ?, tipo = ?, camisa_id = ?, short_id = ?
           WHERE id = ?""",
        (dados.get("time"), dados.get("tipo"), dados.get("camisa_id"),
         dados.get("short_id"), kit_id)
    )
    conexao.commit()
    conexao.close()

    return jsonify({"mensagem": "Kit atualizado!"})


# Remove um kit - PROTEGIDO, precisa da chave
@app.route("/kits/<int:kit_id>", methods=["DELETE"])
@requer_chave
def remover_kit(kit_id):
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM kits WHERE id = ?", (kit_id,))
    if cursor.fetchone() is None:
        conexao.close()
        return jsonify({"erro": "Kit não encontrado"}), 404

    cursor.execute("DELETE FROM kits WHERE id = ?", (kit_id,))
    conexao.commit()
    conexao.close()

    return jsonify({"mensagem": "Kit removido!"})


if __name__ == "__main__":
    criar_tabela()
    # host="0.0.0.0" permite acesso de fora da sua máquina (necessário pra hospedar depois)
    # debug=False é mais seguro pra produção (não mostra detalhe técnico de erro pra quem acessa)
    modo_debug = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=modo_debug)