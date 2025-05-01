import threading
import time
import tkinter as tk
from tkinter import Canvas

# --- Configuración inicial ---
N = 5
VECES_COMER = 6

# Emoticonos y colores de estado mejorados
ESTADOS = {
    'pensando': ('🧠', 'Pensando', '#5DADE2'),
    'esperando': ('⏳', 'Esperando', '#F5B041'),
    'comiendo': ('🍝', 'Comiendo', '#58D68D')
}

# Estados y contadores
filosofos_estado = ['pensando'] * N
comidas_realizadas = [0] * N

# Semáforos para los tenedores
tenedores = [threading.Semaphore(1) for _ in range(N)]
tenedores_estado = [False] * N
mutex = threading.Lock()

# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Cena de Filósofos")
canvas = Canvas(ventana, width=1000, height=1000, bg="white")
canvas.pack()

# Coordenadas ajustadas
coordenadas = [
    (500, 200),
    (740, 360),
    (620, 680),
    (380, 680),
    (260, 360)
]

filosofos_graficos = []
circulos_graficos = []
tenedores_graficos = []
titulos_graficos = []

# Dibujar filósofos y tenedores
for i in range(N):
    x, y = coordenadas[i]
    titulo = canvas.create_text(x, y - 90, text=f"Filósofo {i+1}", font=("Arial", 12), fill="black")
    titulos_graficos.append(titulo)
    c = canvas.create_oval(x-70, y-70, x+70, y+70, fill="#5DADE2", width=3, tags=f"circulo_{i}")
    circulos_graficos.append(c)
    f = canvas.create_text(x, y, text="", font=("Arial", 12), tags=f"filosofo_{i}", justify="center", fill="black")
    filosofos_graficos.append(f)

    x1, y1 = coordenadas[i]
    x2, y2 = coordenadas[(i+1) % N]
    xt, yt = (x1 + x2) / 2, (y1 + y2) / 2
    t = canvas.create_text(xt, yt, text="🥄", font=("Arial", 20), tags=f"tenedor_{i}", fill="gray")
    tenedores_graficos.append(t)

# Texto del mensaje final (oculto inicialmente)
mensaje_final = canvas.create_text(500, 100, text="", font=("Arial", 18), fill="green")

def actualizar_interfaz():
    for i in range(N):
        emote, texto_estado, color = ESTADOS[filosofos_estado[i]]
        comidas = comidas_realizadas[i]
        canvas.itemconfig(f"circulo_{i}", fill=color)
        canvas.itemconfig(
            filosofos_graficos[i],
            text=f"{emote}\n{texto_estado}\n🍽 {comidas}/6"
        )

        color_tenedor = "#EC7063" if tenedores_estado[i] else "#95A5A6"
        canvas.itemconfig(tenedores_graficos[i], fill=color_tenedor)

    ventana.update()

def filosofar(i):
    global comidas_realizadas
    while comidas_realizadas[i] < VECES_COMER:
        with mutex:
            filosofos_estado[i] = 'pensando'
        actualizar_interfaz()
        time.sleep(2.5)

        with mutex:
            filosofos_estado[i] = 'esperando'
        actualizar_interfaz()
        time.sleep(2.5)

        tenedores[i].acquire()
        tenedores[(i+1)%N].acquire()
        with mutex:
            tenedores_estado[i] = True
            tenedores_estado[(i+1)%N] = True

        with mutex:
            filosofos_estado[i] = 'comiendo'
            comidas_realizadas[i] += 1
        actualizar_interfaz()
        time.sleep(4.5)

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

    canvas.itemconfig(mensaje_final, text="✅ Todos los filósofos ya han comido 6 veces.")

    canvas.create_rectangle(250, 850, 750, 910, fill="#27AE60", outline="black", width=3)
    canvas.create_text(500, 880, text="✅ Todos los filósofos han comido 6 veces.", font=("Arial", 16), fill="black")

    # Leyenda
    canvas.create_text(500, 940, text="📘 LEYENDA DE ESTADOS 📘", font=("Arial", 14), fill="black")
    leyendas = [
        ("#5DADE2", "🧠 Pensando"),
        ("#F5B041", "⏳ Esperando"),
        ("#58D68D", "🍝 Comiendo"),
        ("#95A5A6", "🥄 Tenedor libre"),
        ("#EC7063", "🥄 Tenedor en uso")
    ]
    x0, y0 = 80, 960
    for i, (color, texto) in enumerate(leyendas):
        canvas.create_rectangle(x0 + i*180, y0, x0 + 30 + i*180, y0 + 30, fill=color)
        canvas.create_text(x0 + 40 + i*180, y0 + 15, text=texto, anchor="w", font=("Arial", 11), fill="black")

    ventana.update()

threading.Thread(target=iniciar).start()
ventana.mainloop()
