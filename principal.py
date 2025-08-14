import customtkinter as ctk
import sys
from PIL import Image

# Acá intentamos importar la pantalla de marcar archivos.
try:
    from marcar_archivos import mostrar_marcar_archivos  # Acá importamos la pantalla de marcar_archivos.py.
except Exception as e:
    print("Error al importar marcar_archivos:", e)  # Esto me dira si hay algún error al importar marcar_archivos.py.
    sys.exit(1)


# Esta es la configuración global.
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.iconbitmap(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\icono.ico")
app.title("DragoCrypt")
app.geometry("600x600")
app.resizable(False, False)

TITULO_FONT = ctk.CTkFont(size=30, weight="bold")
BOTON_FONT = ctk.CTkFont(size=16)

# ---------------------------
# Scroll Frame principal
# ---------------------------
scroll_frame = ctk.CTkScrollableFrame(app, width=200, height=200)
scroll_frame.pack(fill="both", expand=True, pady=10, padx=10)

imagen_logo = ctk.CTkImage(
    dark_image=Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\icono.png"),
    size=(220, 220)
)

titulo = ctk.CTkLabel(scroll_frame, image=imagen_logo, text="")
titulo.pack(pady=20)

# ---------------------------
# Funciones
# ---------------------------
def limpiar_contenedor(contenedor):
    for widget in contenedor.winfo_children():
        widget.pack_forget()

def mostrar_menu():
    limpiar_contenedor(scroll_frame)

    titulo = ctk.CTkLabel(scroll_frame, image=imagen_logo, text="")
    titulo.pack(pady=20)

    for texto, accion, icono in botones:
        boton = ctk.CTkButton(
            scroll_frame,
            text=texto,
            image=icono,
            compound="left",
            command=accion,
            width=280,
            height=50,
            font=BOTON_FONT
        )
        boton.pack(pady=12)

# Funciones de botones
def marcar_archivos():
    mostrar_marcar_archivos(scroll_frame, mostrar_menu, BOTON_FONT)

def revisar_marcas():
    print("→ Revisar marcas invisibles")

def eliminar_marcas():
    print("→ Eliminiar marcas invisibles")

def registro_usuarios():
    print("→ Registro y control de usuarios")

def configuracion():
    print("→ Ajustes del sistema")

def salir():
    app.destroy()
    sys.exit()

# ---------------------------
# Selector de apariencia
# ---------------------------
modo_map = {
    "Oscuro": "Dark",
    "Claro": "Light",
    "Sistema": "System"
}

def cambiar_apariencia(opcion):
    ctk.set_appearance_mode(modo_map[opcion])

# ---------------------------
# Iconos de botones
# ---------------------------
icono_marcar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\marcar.png"), size=(30, 30))
icono_revisar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\revisar.png"), size=(30, 30))
icono_eliminar = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\eliminar.png"), size=(30, 30))
icono_registro = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\registro.png"), size=(30, 30))
icono_config = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\config.png"), size=(30, 30))
icono_salir = ctk.CTkImage(Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\salir.png"), size=(30, 30))

# ---------------------------
# Botones principales
# ---------------------------
botones = [
    ("Marcar archivos", marcar_archivos, icono_marcar),
    ("Revisar marcas", revisar_marcas, icono_revisar),
    (" Eliminar marcas", eliminar_marcas, icono_eliminar),
    ("Registro de usuarios", registro_usuarios, icono_registro),
    ("Configuración", configuracion, icono_config),
    ("Salir", salir, icono_salir)
]

# Mostrar menú inicial
mostrar_menu()

# ---------------------------
# Selector de tema
# ---------------------------
etiqueta_tema = ctk.CTkLabel(app, text="Modo de apariencia:", font=("Arial", 14))
etiqueta_tema.pack(pady=(5, 0))

selector_tema = ctk.CTkOptionMenu(
    app,
    values=list(modo_map.keys()),
    command=cambiar_apariencia
)
selector_tema.set("Oscuro")
selector_tema.pack(pady=(0, 10))

# ---------------------------
# Mensaje para confirmar que llegó hasta aquí
# ---------------------------
print("Inicializando la ventana de DragoCrypt...")

# ---------------------------
# Iniciar aplicación
# ---------------------------
app.mainloop()