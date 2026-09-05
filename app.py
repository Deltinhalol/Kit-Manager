"""
API do Kit Manager - banco de dados compartilhado
Rode localmente com: python app.py
Depois hospeda no Render/Railway pra ficar público
"""

from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

CAMINHO_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kits.db")


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


# Pega um kit específico pelo ID
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


# Adiciona um novo kit
@app.route("/kits", methods=["POST"])
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


# Edita um kit existente
@app.route("/kits/<int:kit_id>", methods=["PUT"])
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


# Remove um kit
@app.route("/kits/<int:kit_id>", methods=["DELETE"])
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
    app.run(host="0.0.0.0", port=5000, debug=True)
