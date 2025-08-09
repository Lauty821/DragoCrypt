# Acá importo las librerias.
import customtkinter as ctk   # Versión moderna y personalizable de Tkinter.
import sys                    # Permite cerrar el programa correctamente.
from PIL import Image         # Librería para manejar imágenes (Pillow).

# Esta es la configuración global.
ctk.set_appearance_mode("Dark")         # Esto establece el modo visual inicial (Oscuro / Calro / Sistema)
ctk.set_default_color_theme("dark-blue") # Esto cambia la paleta de colores por defecto.

# Acá se crea la ventana principal.
app = ctk.CTk()  # Esto crea la ventana principal de la aplicación.
app.iconbitmap(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\icono.ico")  # Este es el icono que se verá en la barra de título.
app.title("DragoCrypt")       # Este es el texto que aparece en la barra superior de la ventana.
app.geometry("600x600")       # Este es el tamaño inicial de la ventana (ancho x alto en píxeles).
app.resizable(False, False)   # Esto evita que el usuario cambie el tamaño de la ventana.

# Estos son las duentes personalizadas.
TITULO_FONT = ctk.CTkFont(size=30, weight="bold")  # Fuente grande para títulos.
BOTON_FONT = ctk.CTkFont(size=16)                  # Fuente mediana para botones.

# Este es el scrollable flame principal.
# Es un contenedor que permite desplazarse si hay muchos elementos.
# El scroll_frame es la barra que permite desplazarse de arriba hacia abajo en el programa.
scroll_frame = ctk.CTkScrollableFrame(app, width=200, height=200)
scroll_frame.pack(fill="both", expand=True, pady=10, padx=10)

# Esto es el logo que aparece en el programa.
# Esto carga la imagen para modo oscuro (también puede tener una versión para modo claro.)
imagen_logo = ctk.CTkImage(
    dark_image=Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\icono.png"), # Esta es la imagen PNG que aparece como logo en el programa.
    size=(220, 220)  # Este es el tamaño de la imagen en píxeles.
)

# Esto coloca la imagen como un label (sin texto.)
titulo = ctk.CTkLabel(scroll_frame, image=imagen_logo, text="")
titulo.pack(pady=20)



# Estas son las funciones de cada botón.
def marcar_archivos():
    print("→ Abrir ventana para marcar archivos")  # Aquí se pondrá la función real

def revisar_marcas():
    print("→ Revisar marcas invisibles")

def eliminar_marcas():
    print("→ Eliminiar marcas invisibles")

def registro_usuarios():
    print("→ Registro y control de usuarios")

def configuracion():
    print("→ Ajustes del sistema")

def salir():
    app.destroy()  # Esto es lo que cierra la ventana.
    sys.exit()     # Esto finaliza el programa completamente.



# Este es el mapeo de los modos de apariencia.
# Esto es como un diccionario donde se usan nombres en español, pero internamente CTk necesita inglés.
modo_map = {
    "Oscuro": "Dark",
    "Claro": "Light",
    "Sistema": "System"
}

# Esta función cambia el modo visual dependiendo de la opción elegida.
def cambiar_apariencia(opcion):
    ctk.set_appearance_mode(modo_map[opcion])



# Esto carga los iconos de los botones.
icono_marcar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\marcar.png"), size=(30, 30))
icono_revisar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\revisar.png"), size=(30, 30))
icono_eliminar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\eliminar.png"), size=(30, 30))
icono_registro = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\registro.png"), size=(30, 30))
icono_config = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\config.png"), size=(30, 30))
icono_salir = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\salir.png"), size=(30, 30))

# Estos son los botones principales.
botones = [
    ("Marcar archivos", marcar_archivos, icono_marcar),
    ("Revisar marcas", revisar_marcas, icono_revisar),
    (" Eliminar marcas", eliminar_marcas, icono_eliminar),
    ("Registro de usuarios", registro_usuarios, icono_registro),
    ("Configuración", configuracion, icono_config),
    ("Salir", salir, icono_salir)
]



# Esto crea y coloca cada botón dentro del scroll_frame.
for texto, accion, icono in botones:
    boton = ctk.CTkButton(
        scroll_frame,         # Este es el contenedor donde irá.
        text=texto,           # Este es el texto que se muestra.
        image=icono,          # Estos son los iconos PNG (CTkImage.)
        compound="left",      # Esto coloca las imagenes en cierta posición, en este caso esta a la izquierda.
        command=accion,       # Esta es la unción que ejecutará.
        width=280,            # Este es el ancho de los botones.
        height=50,            # Este es el alto de los botones.
        font=BOTON_FONT       # Esta es la fuente personalizada.
    )
    boton.pack(pady=12)       # Este es el espaciado entre los botones.

# Este es el selector de apariencia.
# Este es el texto que explica el menú.
etiqueta_tema = ctk.CTkLabel(app, text="Modo de apariencia:", font=("Arial", 14))
etiqueta_tema.pack(pady=(5, 0))

# Ete es el menú desplegable para elegir el modo de apariencia.
selector_tema = ctk.CTkOptionMenu(
    app,                       # Este es el contenedor.
    values=list(modo_map.keys()),  # Estas son las pciones visibles (en español.)
    command=cambiar_apariencia    # Esta es la función que se ejecuta al cambiar de apariencia.
)
selector_tema.set("Oscuro")    # Este es el valor inicial.
selector_tema.pack(pady=(0, 10))

# Esto es lo que inicia la ventana del programa.
app.mainloop()  # Etse es el bucle principal que mantiene la ventana abierta.