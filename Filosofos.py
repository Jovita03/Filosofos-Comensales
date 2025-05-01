import threading
import time
import tkinter as tk
from tkinter import Canvas

# constantes
N = 5
VECES_COMER = 6

ESTADOS = {
    'pensando': ('🧠', 'Pensando', '#D3CCE3'),
    'esperando': ('⏳', 'Esperando', '#FAE3D9'),
    'comiendo': ('🍝', 'Comiendo', '#C8E6C9')
}

# inicialización de variables
filosofos_estado = ['pensando'] * N
comidas_realizadas = [0] * N

# semaforos para los tenedores
tenedores = [threading.Semaphore(1) for _ in range(N)]
tenedores_estado = [False] * N
mutex = threading.Lock()

# interfaz
ventana = tk.Tk()
ventana.title("Filósofos Comensales")
canvas = Canvas(ventana, width=700, height=650, bg="white")
canvas.pack()

coordenadas = [
    (350, 120),
    (520, 250),
    (440, 470),
    (260, 470),
    (180, 250)
]

filosofos_graficos = []
circulos_graficos = []
tenedores_graficos = []
titulos_graficos = []

# filosofos y tenedores de interfaz
for i in range(N):
    x, y = coordenadas[i]
    titulo = canvas.create_text(x, y - 60, text=f"Filósofo {i+1}", font=("Arial", 12), fill="black")
    titulos_graficos.append(titulo)
    c = canvas.create_oval(x-45, y-45, x+45, y+45, fill="#5DADE2", width=2, tags=f"circulo_{i}")
    circulos_graficos.append(c)
    f = canvas.create_text(x, y, text="", font=("Arial", 11), tags=f"filosofo_{i}", justify="center", fill="black")
    filosofos_graficos.append(f)

    x1, y1 = coordenadas[i]
    x2, y2 = coordenadas[(i+1) % N]
    xt, yt = (x1 + x2) / 2, (y1 + y2) / 2
    t = canvas.create_text(xt, yt, text="🥄", font=("Arial", 18), tags=f"tenedor_{i}", fill="gray")
    tenedores_graficos.append(t)

# descripcion de estados
canvas.create_rectangle(130, 570, 570, 600, fill="#D5F5E3", outline="black", width=2)
canvas.create_text(350, 585, text="📘 Descripcion de estados  📘", font=("Arial", 12), fill="black")

leyendas = [
    ("#D3CCE3", "🧠 Pensando"),
    ("#FAE3D9", "⏳ Esperando"),
    ("#C8E6C9", "🍝 Comiendo"),
    ("#95A5A6", "🥄 Tenedor libre"),
    ("#EC7063", "🍴 Tenedor en uso")
]

x0, y0 = 50, 610
for i, (color, texto) in enumerate(leyendas):
    canvas.create_rectangle(x0 + i*125, y0, x0 + 20 + i*125, y0 + 20, fill=color)
    canvas.create_text(x0 + 25 + i*125, y0 + 10, text=texto, anchor="w", font=("Arial", 10), fill="black")

#mensaje de que ya comieron todos
mensaje_final = canvas.create_text(350, 550, text="", font=("Arial", 14), fill="green")

def actualizar_interfaz():
    for i in range(N):
        emote, texto_estado, color = ESTADOS[filosofos_estado[i]]
        comidas = comidas_realizadas[i]
        canvas.itemconfig(f"circulo_{i}", fill=color)
        canvas.itemconfig(
            filosofos_graficos[i],
            text=f"{emote}\n{texto_estado}\n🍽 {comidas}/6"
        )

        emote_tenedor = "🍴" if tenedores_estado[i] else "🥄"
        color_tenedor = "#EC7063" if tenedores_estado[i] else "#95A5A6"
        canvas.itemconfig(tenedores_graficos[i], text=emote_tenedor, fill=color_tenedor)

    ventana.update()
#logica del filosofo
def filosofar(i):
    global comidas_realizadas
    while comidas_realizadas[i] < VECES_COMER:
        with mutex:
            filosofos_estado[i] = 'pensando'
        actualizar_interfaz()
        time.sleep(2)

        with mutex:
            filosofos_estado[i] = 'esperando'
        actualizar_interfaz()
        time.sleep(2)

        tenedores[i].acquire()
        tenedores[(i+1)%N].acquire()
        with mutex:
            tenedores_estado[i] = True
            tenedores_estado[(i+1)%N] = True

        with mutex:
            filosofos_estado[i] = 'comiendo'
            comidas_realizadas[i] += 1
        actualizar_interfaz()
        time.sleep(3)

        tenedores[i].release()
        tenedores[(i+1)%N].release()
        with mutex:
            tenedores_estado[i] = False
            tenedores_estado[(i+1)%N] = False

    with mutex:
        filosofos_estado[i] = 'pensando'
    actualizar_interfaz()

def iniciar():
    hilos = []
    for i in range(N):
        t = threading.Thread(target=filosofar, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    canvas.itemconfig(mensaje_final, text="✅ Todos los filósofos han comido 6 veces")

threading.Thread(target=iniciar).start()
ventana.mainloop()
