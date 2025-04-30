import threading
import time
import tkinter as tk
from tkinter import Canvas


N = 5
VECES_COMER = 6


ESTADOS = {
    'pensando': ('😐', 'Pensando'),
    'esperando': ('🍴', 'Esperando tenedores'),
    'comiendo': ('😋', 'Comiendo')
}


filosofos_estado = ['pensando'] * N
comidas_realizadas = [0] * N

# semsforos para tenedores
tenedores = [threading.Semaphore(1) for _ in range(N)]
mutex = threading.Lock()

ventana = tk.Tk()
ventana.title("Problema de los Filósofos Comensales")
canvas = Canvas(ventana, width=900, height=800, bg="white")
canvas.pack()

coordenadas = [
    (450, 150),
    (700, 300),
    (600, 600),
    (300, 600),
    (200, 300)
]

filosofos_graficos = []
tenedores_graficos = []

#filósofos y tenedores
for i in range(N):
    x, y = coordenadas[i]
    f = canvas.create_text(x, y, text="", font=("Arial", 18), tags=f"filosofo_{i}", justify="center")
    filosofos_graficos.append(f)

    
    x1, y1 = coordenadas[i]
    x2, y2 = coordenadas[(i+1) % N]
    xt, yt = (x1 + x2) / 2, (y1 + y2) / 2
    t = canvas.create_text(xt, yt, text="🥄", font=("Arial", 20), tags=f"tenedor_{i}")
    tenedores_graficos.append(t)

def actualizar_interfaz():
    for i in range(N):
        emote, texto_estado = ESTADOS[filosofos_estado[i]]
        comidas = comidas_realizadas[i]
        canvas.itemconfig(
            filosofos_graficos[i],
            text=f"Filósofo {i+1}\n{emote} {texto_estado}\nComidas: {comidas}"
        )
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
            filosofos_estado[i] = 'comiendo'
            comidas_realizadas[i] += 1
        actualizar_interfaz()
        time.sleep(4)

        tenedores[i].release()
        tenedores[(i+1)%N].release()

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

    canvas.create_text(450, 750, text="\u2714 Todos los filósofos han comido 6 veces.", font=("Arial", 20, "bold"), fill="green")
    ventana.update()


threading.Thread(target=iniciar).start()
ventana.mainloop()
