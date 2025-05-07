import threading
import time
import tkinter as tk
from tkinter import Canvas

# Constantes
N = 5
VECES_COMER = 6

ESTADOS = {
    'pensando': ('🧠', 'Pensando', '#D3CCE3'),
    'esperando': ('⏳', 'Esperando', '#FAE3D9'),
    'comiendo': ('🍝', 'Comiendo', '#C8E6C9')
}

filosofos_estado = ['pensando'] * N #Lista que guarda el estado actual de cada filósofo
comidas_realizadas = [0] * N #Lista que cuenta cuántas veces ha comido cada filósofo
tenedores = [threading.Semaphore(1) for _ in range(N)] # Lista de tenedores, cada tenedor es un semáforo

# Interfaz
ventana = tk.Tk()
ventana.title("Cena de Filósofos")
canvas = Canvas(ventana, width=700, height=650, bg="white")
canvas.pack()

coordenadas = [ # Coordenadas de los filósofos
    (350, 120),
    (520, 250),
    (440, 470),
    (260, 470),
    (180, 250)
]

filosofos_graficos = [] # Lista para guardar los objetos de los filósofos
circulos_graficos = []
tenedores_graficos = []
titulos_graficos = []

# Dibujar filósofos y tenedores
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

# Leyenda
canvas.create_rectangle(130, 570, 570, 600, fill="#D5F5E3", outline="black", width=2)
canvas.create_text(350, 585, text="📘 LEYENDA DE ESTADOS 📘", font=("Arial", 12), fill="black")

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

mensaje_final = canvas.create_text(350, 550, text="", font=("Arial", 14), fill="green")

mutex = threading.Lock() # Mutex para proteger el acceso a la lista de estados y comidas realizadas

def actualizar_interfaz():
    for i in range(N):
        emote, texto_estado, color = ESTADOS[filosofos_estado[i]]
        comidas = comidas_realizadas[i]
        canvas.itemconfig(f"circulo_{i}", fill=color)
        canvas.itemconfig(
            filosofos_graficos[i],
            text=f"{emote}\n{texto_estado}\n🍽 {comidas}/{VECES_COMER}"
        )

    for i in range(N): 
        izquierdo = i
        derecho = (i + 1) % N
        usado = (filosofos_estado[izquierdo] == 'comiendo' or
                 filosofos_estado[derecho] == 'comiendo')
        emote_tenedor = "🍴" if usado else "🥄"
        color_tenedor = "#EC7063" if usado else "#95A5A6"
        canvas.itemconfig(tenedores_graficos[i], text=emote_tenedor, fill=color_tenedor)

def actualizar_interfaz_seguro(): #Actualiza el emoji y color del tenedor si está en uso o libre
    ventana.after(0, actualizar_interfaz)

def filosofar(i):
    while comidas_realizadas[i] < VECES_COMER: #ciclo que se repite hasta que el filósofo coma 6 veces
        with mutex:  #Sirve para proteger el acceso a datos compartidos entre hilos, evitando condiciones de carrera
            filosofos_estado[i] = 'pensando'
        actualizar_interfaz_seguro()
        time.sleep(4)

        with mutex: #Objeto que garantiza que solo un hilo acceda a una sección crítica a la vez
            filosofos_estado[i] = 'esperando'
        actualizar_interfaz_seguro()
        time.sleep(4)

        tenedores[i].acquire() # agarra el tenedor izquierdo y ademas es el mrtodo que bloquea el hilo hasta que pueda obtener el recurso 
        tenedores[(i+1) % N].acquire()  #

        with mutex:
            filosofos_estado[i] = 'comiendo'
            comidas_realizadas[i] += 1
        actualizar_interfaz_seguro()
        time.sleep(6)

        tenedores[i].release()
        tenedores[(i+1) % N].release() #libera el tenedor izquierdo y derecho

        with mutex:
            filosofos_estado[i] = 'pensando'
        actualizar_interfaz_seguro()

    # Verifica si todos terminaron
    if all(c == VECES_COMER for c in comidas_realizadas): # si para cada comida realizada es igual a 6 entonces se mostrara el mensaje 
        ventana.after(0, lambda: canvas.itemconfig(mensaje_final, text="✅ Todos los filósofos han comido 6 veces"))

def iniciar():
    for i in range(N):
        t = threading.Thread(target=filosofar, args=(i,))
        t.daemon = True  # hace que el hilo termine cuando cierre la ventana.
        t.start()

# Iniciar después de que la ventana arranca
ventana.after(100, iniciar)
ventana.mainloop()
