import turtle

tela = turtle.Screen()
tela.bgcolor("#1a1a2e")  # fundo escuro pra destacar o coração
tela.title("Coração fofo <3")

t = turtle.Turtle()
t.speed(8)
t.hideturtle()  # esconde o "bichinho" no final, fica mais limpo
t.pensize(2)

t.penup()
t.goto(0, -150)
t.pendown()

t.color("#ff1493", "#ff69b4")  # contorno rosa forte, preenchimento rosa claro
t.begin_fill()

t.left(50)
t.forward(200)
t.circle(75, 200)
t.right(140)
t.circle(75, 200)
t.forward(200)

t.end_fill()

turtle.done()