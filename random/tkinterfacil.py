import FreeSimpleGUI as sg

layout = [
    [sg.Text("Digite seu nome:")],
    [sg.Input(key="-NOME-")],
    [sg.Button("Enviar"), sg.Button("Sair")]
]

janela = sg.Window("Meu primeiro app", layout)

while True:
    evento, valores = janela.read()

    if evento in (sg.WIN_CLOSED, "Sair"):
        break

    if evento == "Enviar":
        nome = valores["-NOME-"]
        sg.popup(f"Olá, {nome}! 🐢")

janela.close()