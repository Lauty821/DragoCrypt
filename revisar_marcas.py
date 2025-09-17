# ---------------------- IMPORTACIONES ----------------------
# Importa la biblioteca "customtkinter" para crear interfaces gráficas modernas.
import customtkinter as ctk

"""
Importa desde tkinter el módulo "filedialog" que permite abrir cuadros de diálogo
para seleccionar archivos o carpetas en el sistema operativo.
"""
from tkinter import filedialog

# Importa la biblioteca estándar "os" para trabajar con rutas, nombres de archivos y funciones del sistema operativo.
import os


# Delimitador que indica el inicio de la marca dentro de un archivo.
DELIM_INI = b"<<CTK_MARK_BEGIN>>"
# Delimitador que indica el final de la marca dentro de un archivo.
DELIM_FIN = b"<<CTK_MARK_END>>"

# Tamaño máximo de bytes a leer desde el final de un archivo.
MAX_TAIL = 8192

# Proporción mínima de caracteres imprimibles (puede usarse para validaciones futuras)
MIN_PRINTABLE_RATIO = 0.85



# ---------------------- FUNCIONES AUXILIARES ----------------------
def _leer_tail(archivo, max_tail=MAX_TAIL):
    """
    Lee los últimos bytes de un archivo hasta un máximo definido por max_tail.
    - archivo: ruta del archivo a leer.
    - max_tail: cantidad máxima de bytes a leer desde el final.
    Retorna: bytes leídos del final del archivo.
    """

    with open(archivo, "rb") as f:
        # Mueve el cursor al final del archivo
        f.seek(0, os.SEEK_END)
        # Obtiene el tamaño total del archivo
        size = f.tell()

        if size > max_tail:
            # Si el archivo es más grande que max_tail, se posiciona max_tail bytes antes del final
            f.seek(-max_tail, os.SEEK_END)
        else:
            # Si el archivo es más pequeño, se posiciona al inicio
            f.seek(0, os.SEEK_SET)
        # Devuelve los bytes leídos
        return f.read()


def _extraer_por_delimitadores(datos_tail: bytes):
    """
    Busca la marca delimitada dentro de los bytes leídos del final del archivo.
    - datos_tail: bytes leídos del final del archivo.
    Retorna: texto de la marca si se encuentra, o None.
    """
    if not datos_tail:
        return None  # Retorna None si no hay datos.

    # Busca el índice de inicio del delimitador.
    ini = datos_tail.find(DELIM_INI)
    if ini == -1:
        return None  # No encontró el inicio.
    ini += len(DELIM_INI)  # Ajusta el índice al final del delimitador de inicio.

    # Busca el índice del delimitador final.
    fin = datos_tail.find(DELIM_FIN, ini)
    if fin == -1:
        return None  # No encontró el final.

    # Extrae el bloque de bytes que contiene la marca.
    bloque = datos_tail[ini:fin]
    try:
        # Intenta decodificarlo como UTF-8 y eliminar espacios al inicio y final.
        texto = bloque.decode("utf-8", errors="strict").strip()
        return texto if texto else None  # Retorna texto o None si está vacío.
    except UnicodeDecodeError:
        return None  # Retorna None si falla la decodificación.


def extraer_marca_delimitada(archivo):
    """
    Función principal para obtener la marca delimitada de un archivo.
    - archivo: ruta del archivo a revisar.
    Retorna: texto de la marca o None.
    """
    tail = _leer_tail(archivo, MAX_TAIL)  # Lee los últimos bytes del archivo.
    return _extraer_por_delimitadores(tail)  # Extrae la marca usando los delimitadores.


# ---------------------- FUNCIÓN PARA MOSTRAR LA PANTALLA DE REVISAR ARCHIVOS ----------------------
def mostrar_revisar_marcas(parent, volver_callback, boton_font):
    """
    Crea y muestra la interfaz gráfica para seleccionar y marcar archivos.
    - parent: contenedor principal donde se colocarán los elementos gráficos.
    - volver_callback: función que se ejecutará cuando se presione el botón "Volver".
    - boton_font: tipo de fuente (familia, tamaño, estilo) que se usará en los botones.
    """

    # Oculta todos los widgets que ya existían en el contenedor,
    for widget in parent.winfo_children():
        widget.pack_forget()



    # ---------------------- TÍTULO ----------------------
    # Crea una etiqueta (Label) con el título de la pantalla.
    titulo = ctk.CTkLabel(
        parent,  # Contenedor donde se coloca el texto.
        text="Revisar Marcas (solo delimitadas)",  # Texto que se muestra.
        font=("Arial", 22, "bold")  # Fuente: tamaño 22, negrita ("bold").
    )
    # Empaqueta (muestra) el título con margen vertical.
    titulo.pack(pady=12)


    # ---------------------- LISTA DE ARCHIVOS SELECCIONADOS ----------------------
    # Lista en memoria donde se guardan las rutas completas de los archivos que el usuario elija.
    lista_archivos = []


    # Crea un panel (frame) con fondo blanco para contener la lista de archivos.
    panel_widget = ctk.CTkTextbox(
        parent,  # Contenedor principal.
        width=500,  # Ancho de 500 píxeles.
        height=200,  # Alto de 200 píxeles.
        fg_color="white",  # Color de fondo (blanco).
        text_color="black"  # Color del texto (negro).
    )
    # Se deshabilita la edición
    panel_widget.configure(state="disabled")
    # Empaqueta el panel con padding vertical de 8 píxeles.
    panel_widget.pack(pady=8)



    # ---------------------- MENSAJES ----------------------
    # Crea una etiqueta para mostrar mensajes temporales (advertencias, confirmaciones, errores).
    mensaje_label = ctk.CTkLabel(
        parent,  # Contenedor principal.
        text="",  # Empieza vacío.
        font=("Arial", 14, "bold")  # Fuente Arial, tamaño 14, en negrita.
    )
    # Muestra la etiqueta con un margen superior de 5 píxeles y sin margen inferior.
    mensaje_label.pack(pady=(5, 0))


    # ---------------------- FUNCIÓN PARA MOSTRAR MENSAJES ----------------------
    def mostrar_mensaje(texto, color):
        """
        Muestra un mensaje en "mensaje_label" con un color específico y lo borra después de 3,5 segundos.
        """

        # Cambia el texto y el color de la etiqueta.
        mensaje_label.configure(text=texto, text_color=color)
        # Usa "after" para ejecutar una función después de 3.3 segundos.
        # Aquí se usa para vaciar el texto después del tiempo.
        parent.after(3300, lambda: mensaje_label.configure(text=""))



    # ---------------------- FUNCIÓN PARA ACTUALIZAR PANEL ----------------------
    def actualizar_panel_lista():
        """
        Actualiza el contenido del cuadro del panel con los nombres de los archivos en 'lista_archivos'.
        """

        # Activa la edición temporalmente para poder modificar el contenido.
        panel_widget.configure(state="normal")  
        # Borra todo lo que había antes en el panel.
        panel_widget.delete("1.0", "end")

        # Recorre cada archivo en la lista y muestra solo el nombre (sin ruta).
        for archivo in lista_archivos:
            panel_widget.insert("end", os.path.basename(archivo) + "\n")  
        # Vuelve a ponerlo en modo solo lectura.
        panel_widget.configure(state="disabled")



    # ---------------------- FUNCIÓN PARA SELECCIONAR ARCHIVOS ----------------------
    def seleccionar_archivos():
        """
        Abre un cuadro de diálogo para seleccionar uno o varios archivos y los agrega a la lista.
        """
        
        # Muestra el explorador de archivos para elegir múltiples archivos.
        seleccionados = filedialog.askopenfilenames( 
        title="Seleccionar archivos",  # Título de la ventana emergente.
        filetypes=[("Todos los archivos", "*.*")]  # Permite seleccionar cualquier tipo de archivo.
        )

         # Si el usuario no selecciona nada, la función termina aquí.
        if not seleccionados:
            return

        lista_archivos.clear()  # Limpia lista actual.
        lista_archivos.extend(seleccionados)  # Agrega archivos seleccionados.
        actualizar_panel_lista()  # Refresca el panel de resultados.
        # Activa botones según si hay archivos en la lista.
        boton_quitar.configure(state="normal" if lista_archivos else "disabled")
        boton_revisar.configure(state="normal" if lista_archivos else "disabled")

    def quitar_archivos():
        """
        Quita los archivos seleccionados en el panel.
        """
        if not panel_widget.tag_ranges("sel"):
            mostrar_mensaje("⚠ Debes seleccionar al menos un archivo", "yellow")
            return  # Si no hay selección, termina.

        # Obtiene los nombres seleccionados en el cuadro de resultados.
        seleccion = panel_widget.get("sel.first", "sel.last").strip().split("\n")
        # Filtra rutas de la lista principal que coinciden con los nombres seleccionados.
        rutas_a_eliminar = [ruta for ruta in lista_archivos if os.path.basename(ruta) in seleccion]
        for ruta in rutas_a_eliminar:
            if ruta in lista_archivos:
                lista_archivos.remove(ruta)
        actualizar_panel_lista()  # Refresca el panel de resultados.
        # Activa o desactiva botones según haya archivos en la lista.
        boton_quitar.configure(state="normal" if lista_archivos else "disabled")
        boton_revisar.configure(state="normal" if lista_archivos else "disabled")

    # Configura colores de etiquetas dentro del Textbox.
    panel_widget.tag_config("ok", foreground="green")
    panel_widget.tag_config("error", foreground="red")



    # ---------------------- FUNCIÓN PARA REVISAR MARCAS ----------------------
    def revisar_archivos():
        """
        Recorre todos los archivos en 'lista_archivos' y muestra su marca delimitada o error.
        """

        if not lista_archivos:
            return  # Si no hay archivos, termina.

        panel_widget.configure(state="normal")  # Habilita edición temporal.
        panel_widget.delete("1.0", "end")  # Borra contenido previo.

        # Recorre cada archivo
        for ruta in lista_archivos:
            nombre = os.path.basename(ruta)  # Obtiene solo el nombre del archivo.
            try:
                marca = extraer_marca_delimitada(ruta)  # Intenta extraer la marca.
            except Exception as e:
                # Muestra error si falla la extracción.
                panel_widget.insert("end", f"❌ {nombre} → Error: {e}\n", "error")
                continue

            # Muestra resultado según haya marca o no
            if marca:
                panel_widget.insert("end", "✅ ", "ok")  # Símbolo verde.
                panel_widget.insert("end", f"{nombre} → {marca}\n")  # Texto de marca.
            else:
                panel_widget.insert("end", "❌ ", "error")  # Símbolo rojo.
                panel_widget.insert("end", f"{nombre} → No se detectó ninguna marca\n")  # Mensaje.



        # ---------------------- LIMPIEZA AUTOMÁTICA ----------------------
        def limpieza():
            """
            Limpia la lista de archivos y el panel después de revisar.
            """

            lista_archivos.clear()  # Borra lista de archivos.
            panel_widget.configure(state="normal")
            panel_widget.delete("1.0", "end")  # Borra contenido del panel.
            panel_widget.configure(state="disabled")
            boton_quitar.configure(state="disabled")
            boton_revisar.configure(state="disabled")

        parent.after(5500, limpieza)  # Ejecuta limpieza después de 5.5 segundos.



    # ---------------------- BOTÓN PARA QUITAR ARCHIVOS DEL PANEL ----------------------
    boton_quitar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Quitar archivos del panel",  # Texto que muestra el botón.
        command=quitar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        state="disabled"  # Comienza deshabilitado hasta que haya archivos en la lista.
    )
    boton_quitar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.



    # ---------------------- BOTÓN PARA REVISAR MARCAS ----------------------
    boton_revisar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Revisar marcas",  # Texto que muestra el botón.
        command=revisar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        state="disabled"  # Comienza deshabilitado hasta que haya archivos en la lista.
    )
    boton_revisar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.


    # ---------------------- BOTÓN PARA VOLVER AL MENÚ PRINCIPAL ----------------------
    boton_volver = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Volver al menú principal",  # Texto que muestra el botón.
        command=volver_callback,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_volver.pack(pady=6)