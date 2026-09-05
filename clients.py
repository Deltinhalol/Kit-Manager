"""
Exemplo de como seu app Tkinter deve conversar com a API
Troque URL_BASE pelo endereço real depois que hospedar (ex: https://seu-app.onrender.com)
"""

import requests

URL_BASE = "http://127.0.0.1:5000"  # local pra testar; depois troca pra URL do Render/Railway


def listar_kits(time=None):
    params = {"time": time} if time else {}
    resposta = requests.get(f"{URL_BASE}/kits", params=params)
    return resposta.json()


def adicionar_kit(time, tipo, camisa_id, short_id):
    dados = {
        "time": time,
        "tipo": tipo,
        "camisa_id": camisa_id,
        "short_id": short_id
    }
    resposta = requests.post(f"{URL_BASE}/kits", json=dados)
    return resposta.json()


def editar_kit(kit_id, time, tipo, camisa_id, short_id):
    dados = {
        "time": time,
        "tipo": tipo,
        "camisa_id": camisa_id,
        "short_id": short_id
    }
    resposta = requests.put(f"{URL_BASE}/kits/{kit_id}", json=dados)
    return resposta.json()


def remover_kit(kit_id):
    resposta = requests.delete(f"{URL_BASE}/kits/{kit_id}")
    return resposta.json()


# Exemplo de uso (pode chamar essas funções nos seus botões do Tkinter)
if __name__ == "__main__":
    # Adicionando um kit de teste
    resultado = adicionar_kit("Flamengo", "home", "00001234", "00005678")
    print("Adicionado:", resultado)

    # Listando todos os kits do Flamengo
    kits_flamengo = listar_kits("Flamengo")
    print("Kits do Flamengo:", kits_flamengo)
