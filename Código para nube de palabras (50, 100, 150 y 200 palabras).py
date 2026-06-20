import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog, messagebox


#  Tema Interfaz

BG_MAIN = "#fff3e8"       # fondo ventana
BG_FRAME = "#ffe2cc"      # fondo marco
FG_TITLE = "#cc6e3c"      # títulos
FG_TEXT = "#7a4a2b"       # texto normal
BTN_BG = "#ffd4b8"        # botón normal
BTN_BG_ACTIVE = "#f7bb94" # hover botón


# ESTADOS

selected_background = None
selected_colormap = None


# FUNCIÓN — GENERAR NUBES

def generar_nubes():
    global selected_background, selected_colormap

    if selected_background is None:
        messagebox.showwarning("Falta fondo", "Por favor selecciona un fondo primero.")
        return

    if selected_colormap is None:
        messagebox.showwarning("Falta estilo", "Por favor selecciona un estilo de color.")
        return

    messagebox.showinfo(
        "Archivo",
        "Por favor, elige un archivo .txt para crear la nube de palabras."
    )

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo .txt",
        filetypes=[("Archivos de texto", "*.txt")]
    )

    if not ruta:
        messagebox.showerror("Error", "No se seleccionó ningún archivo.")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read().lower()

    tokens = re.findall(r'\b[a-záéíóúüñ]+\b', texto)

    # Stopwords unidas
    stopwords_es = {
        "de","la","que","el","en","y","a","los","se","del","las","por","un","para",
        "con","no","una","su","al","lo","como","más","pero","sus","le","ya","o",
        "este","sí","porque","esta","entre","cuando","muy","sin","sobre","también",
        "me","hasta","hay","donde","quien","desde","todo","nos","durante","todos",
        "uno","les","ni","contra","otros","ese","eso","ante","ellos","e","esto",
        "mí","antes","algunos","qué","unos","yo","otro","otras","otra","él","tanto",
        "esa","estos","mucho","quienes","nada","muchos","cual","poco","ella","estar",
        "estas","algunas","algo","nosotros","mi","mis","tú","te","ti","tu","tus",
        "ellas","nosotras","vosotros","vosotras","os","mío","mía","míos","mías",
        "tuyo","tuya","tuyos","tuyas","suyo","suya","suyos","suyas","nuestro",
        "nuestra","nuestros","nuestras","vuestro","vuestra","vuestros","vuestras",
        "esos","esas","estoy","estás","está","estamos","estáis","están","esté",
        "estés","estemos","estéis","estén","estaré","estarás","estará","estaremos",
        "estaréis","estarán","he","has","ha","hemos","habéis","han","haya","hayas",
        "hayamos","hayan","ser","soy","eres","es","somos","sois","son","sea","seas",
        "seamos","seáis","sean", "si", "cómo", "cada", "fue", "través", "tienen",
        "puede","tener", "vez", "además", "tiene", "manera", "solo", "así", "primer",
        "pueden", "dos", "ii", "cal", "dentro", "fuera", "partir", "mismo", "aún",
        "debe", "sólo", "cual", "cuales", "cuanto", "cuantos", "siendo",
        "ser", "estar", "ci", "sino", "si no", "tal vez", "iii", "hace", "hacer",
        "dar", "tres", "cuatro", "cinco", "hacia", "sino", "fueron", "mismo",
        "sido", "fue", "será", "CI", "tal", "bajo", "mientras", "iv", "v", "vi", "vii", "s",
        "fin", "todos", "todas", "todes", "realizó","aunque", "presentan", "respecto", "menos",
        "mas", "igual", "sin", "embargo", "alto", "alta", "según", "forma", "paso", "pasos",
        "permite","acuerdo","anterior","posterior","marco"
    }

    stopwords_en = {
        "the","a","an","and","or","of","in","on","for","to","from","at","with","as",
        "by","that","this","it","is","are","was","were","be","been","being","have",
        "has","had","having","do","does","did","doing","will","would","should",
        "can","could","may","might","must","not","so","if","than","then","too",
        "very","there","here","their","they","them","these","those","he","she",
        "his","her","hers","its","we","our","ours","you","your","yours","me","my",
        "mine","what","which","who","whom","when","where","why","how","all","any",
        "both","each","few","more","most","other","some","such","no","nor","only",
        "own","same","just","because","also","once","while","into","over","after",
        "before","again","further","off","up","down","out","about","above","below",
        "between","under","against","during","through","until","without","across"
    }

    stop_words = stopwords_es.union(stopwords_en)

    tokens_limpios = [t for t in tokens if t not in stop_words]
    frecuencias = Counter(tokens_limpios)

    cantidades = [50, 100, 150, 200]

    for cant in cantidades:
        nube = WordCloud(
            width=1600,
            height=900,
            background_color=selected_background,
            colormap=selected_colormap,
            max_words=cant,
            relative_scaling=0.5
        ).generate_from_frequencies(frecuencias)

        plt.figure(figsize=(10, 6))
        plt.imshow(nube, interpolation="bilinear")
        plt.axis("off")
        plt.title(
            f"Nube de palabras ({cant} palabras)\nEstilo: {selected_colormap} | Fondo: {selected_background}",
            fontsize=14
        )
        plt.show()

        nombre_archivo = f"nube_{cant}_palabras.png"
        nube.to_file(nombre_archivo)

    messagebox.showinfo("Listo", "Todas las nubes fueron generadas correctamente.")


# CALLBACKS

def elegir_fondo(valor, etiqueta):
    global selected_background
    selected_background = valor
    label_fondo.config(text=f"Fondo seleccionado: {etiqueta}")


def elegir_estilo(valor, etiqueta):
    global selected_colormap
    selected_colormap = valor
    label_estilo.config(text=f"Estilo seleccionado: {etiqueta}")



# Interfaz

root = tk.Tk()
root.title("Generador de Nubes – Durazno Pastel")
root.configure(bg=BG_MAIN)
root.geometry("520x520")

frame = tk.Frame(root, bg=BG_FRAME, bd=2, relief="flat")
frame.pack(expand=True, fill="both", padx=20, pady=20)


label_title = tk.Label(
    frame,
    text="Generador de Nubes de Palabras",
    bg=BG_FRAME, fg=FG_TITLE,
    font=("Segoe UI Semibold", 15)
)
label_title.pack(pady=10)

# Elegir Fondo
tk.Label(frame,
    text="1) Selecciona un fondo:",
    bg=BG_FRAME, fg=FG_TITLE,
    font=("Segoe UI Semibold", 11)
).pack(pady=(5, 2))

def boton(texto, comando):
    return tk.Button(
        frame, text=texto, width=26,
        font=("Segoe UI", 10),
        relief="flat",
        bg=BTN_BG,
        fg=FG_TEXT,
        activebackground=BTN_BG_ACTIVE,
        command=comando
    )

boton("Fondo negro", lambda: elegir_fondo("black", "Negro")).pack(pady=2)
boton("Fondo blanco", lambda: elegir_fondo("white", "Blanco")).pack(pady=2)
boton("Fondo durazno pastel", lambda: elegir_fondo(BG_MAIN, "Durazno pastel")).pack(pady=2)

label_fondo = tk.Label(frame, text="Fondo seleccionado: (ninguno)", bg=BG_FRAME, fg=FG_TEXT)
label_fondo.pack(pady=8)

# Elegir Estilo
tk.Label(frame,
    text="2) Selecciona un estilo de color:",
    bg=BG_FRAME, fg=FG_TITLE,
    font=("Segoe UI Semibold", 11)
).pack(pady=(10, 2))

boton("Estilo Purples", lambda: elegir_estilo("Purples", "Purples")).pack(pady=2)
boton("Estilo Dark2", lambda: elegir_estilo("Dark2", "Dark2")).pack(pady=2)
boton("Estilo RdPu_r", lambda: elegir_estilo("RdPu_r", "RdPu_r")).pack(pady=2)

label_estilo = tk.Label(frame, text="Estilo seleccionado: (ninguno)", bg=BG_FRAME, fg=FG_TEXT)
label_estilo.pack(pady=10)

# Generar nubes de palabras
tk.Button(
    frame,
    text="Generar nubes de palabras",
    width=30,
    height=2,
    bg=BTN_BG, fg=FG_TEXT,
    relief="flat",
    activebackground=BTN_BG_ACTIVE,
    font=("Segoe UI Semibold", 11),
    command=generar_nubes
).pack(pady=15)

root.mainloop()
