# Importa la librería CustomTkinter con el alias 'ctk' para crear interfaces gráficas con estilo moderno.
import customtkinter as ctk

# Importa el módulo 'filedialog' de tkinter para abrir cuadros de diálogo que permiten seleccionar archivos.
from tkinter import filedialog

# Importa el módulo 'os' para manejar rutas, nombres de archivos y operaciones con el sistema operativo.
import os

# Importa 'string' que contiene utilidades relacionadas con cadenas de texto, como conjuntos de caracteres.
import string


# --- Configuración opcional de delimitadores para detectar marcas en archivos ---
# Estos delimitadores sirven para encapsular el texto de una marca dentro de un archivo.
DELIM_INI = b"<<CTK_MARK_BEGIN>>"  # Delimitador inicial (en formato bytes).
DELIM_FIN = b"<<CTK_MARK_END>>"  # Delimitador final (en formato bytes).

# --- Parámetros de lectura ---
MAX_TAIL = 8192  # Máximo de bytes que se leerán desde el final del archivo (8 KB).
MIN_PRINTABLE_RATIO = 0.85  # Porcentaje mínimo de caracteres imprimibles para considerar un texto legible.



# ---------------------- FUNCIÓN PARA LEER EL FINAL (TAIL) DE UN ARCHIVO ----------------------
def _leer_tail(archivo, max_tail=MAX_TAIL):
    with open(archivo, "rb") as f:  # Abre el archivo en modo binario de solo lectura.
        f.seek(0, os.SEEK_END)  # Mueve el puntero al final del archivo.
        size = f.tell()  # Obtiene el tamaño total del archivo en bytes.
        if size > max_tail:  # Si el archivo es más grande que max_tail...
            f.seek(-max_tail, os.SEEK_END)  # Mueve el puntero 'max_tail' bytes antes del final.
        else:
            f.seek(0, os.SEEK_SET)  # Si no, mueve el puntero al inicio del archivo.
        return f.read()  # Lee y retorna el contenido desde la posición actual.



# ---------------------- FUNCIÓN PARA COMPROBAR SI UN TEXTO ES IMPRIMIBLE ----------------------
def _es_printable_text(s: str) -> bool:
    if not s:  # Si la cadena está vacía, no es válida.
        return False
    imprimibles = sum(ch.isprintable() for ch in s)  # Cuenta cuántos caracteres son imprimibles.
    return (imprimibles / len(s)) >= MIN_PRINTABLE_RATIO  # Retorna True si la proporción supera el mínimo.



# ---------------------- FUNCIÓN PARA EXTRAR UNA MARCA USANDO DELIMITADORES ----------------------
def _extraer_por_delimitadores(datos_tail: bytes):
    ini = datos_tail.find(DELIM_INI)  # Busca el delimitador inicial en el contenido.
    if ini == -1:  # Si no se encuentra, retorna None.
        return None
    ini += len(DELIM_INI)  # Avanza el índice para saltar el delimitador inicial.
    fin = datos_tail.find(DELIM_FIN, ini)  # Busca el delimitador final desde la posición 'ini'.
    if fin == -1:  # Si no se encuentra, retorna None.
        return None
    bloque = datos_tail[ini:fin]  # Extrae el bloque de bytes entre los delimitadores.
    try:
        texto = bloque.decode("utf-8", errors="strict").strip()  # Decodifica a UTF-8 y limpia espacios.
        return texto if texto else None  # Retorna el texto si no está vacío.
    except UnicodeDecodeError:  # Si hay error de decodificación, retorna None.
        return None



# ---------------------- FUNCIÓN PARA EXTRAER UNA MARCA MEDIANTE HEURÍSTICA SI NO HAY DELIMITADORES ----------------------
def _extraer_por_heuristica(datos_tail: bytes):
    if not datos_tail:  # Si no hay datos, retorna None.
        return None
    texto_tail = datos_tail.decode("utf-8", errors="ignore")  # Decodifica ignorando errores.
    if not texto_tail:  # Si no hay texto decodificado, retorna None.
        return None
    
    partes = texto_tail.splitlines()  # Divide el texto en líneas.
    if partes:  # Si hay líneas...
        candidato = partes[-1].strip()  # Toma la última línea.
        if not candidato and len(partes) >= 2:  # Si la última está vacía, toma la penúltima.
            candidato = partes[-2].strip()
        if candidato and _es_printable_text(candidato):  # Si es texto imprimible...
            return candidato  # Retorna la línea encontrada.

    # Si no hay líneas claras, intenta extraer caracteres imprimibles desde el final.
    acumulado = []
    for ch in reversed(texto_tail):  # Recorre el texto desde el final.
        if ch.isprintable():  # Si el carácter es imprimible...
            acumulado.append(ch)  # Lo agrega a la lista acumulada.
        else:
            break  # Si encuentra uno no imprimible, se detiene.
    if acumulado:
        candidato = "".join(reversed(acumulado)).strip()  # Reconstruye el texto en orden correcto.
        if candidato and _es_printable_text(candidato):  # Verifica que sea legible.
            return candidato

    return None  # Si no se encuentra nada, retorna None.



# ---------------------- FUNCIÓN PRINCIPAL QUE INTENTA EXTRAER UNA MARCA GENÉRICA DE UN ARCHIVO ----------------------
def extraer_marca_generica(archivo):
    tail = _leer_tail(archivo, MAX_TAIL)  # Lee el final del archivo.
    marca = _extraer_por_delimitadores(tail)  # Intenta extraer por delimitadores.
    if marca:
        return marca  # Si la encuentra, la retorna.
    return _extraer_por_heuristica(tail)  # Si no, intenta por heurística.



# ---------------------- FUNCIÓN PARA MOSTRAR LA PANTALLA DE REVISAR MARCAS ----------------------
def mostrar_revisar_marcas(parent, volver_callback, boton_font):
    # Elimina todos los widgets actuales del contenedor 'parent'.
    for widget in parent.winfo_children():
        widget.pack_forget()

    # Etiqueta de título
    titulo = ctk.CTkLabel(
        parent,  # Contenedor principal.
        text="Revisar Marcas (detección genérica)",  # Texto mostrado.
        font=("Arial", 22, "bold")  # Fuente Arial, tamaño 20, negrita.
    )
    titulo.pack(pady=12)  # Agrega el widget con un margen vertical de 12 píxeles.

    # Lista que almacenará las rutas de los archivos seleccionados.
    lista_archivos = []

    # Panel donde se mostrarán los archivos y resultados.
    resultados_widget = ctk.CTkTextbox(
        parent,
        width=500,  # Ancho en píxeles.
        height=300,  # Alto en píxeles.
        fg_color="white",  # Fondo blanco.
        text_color="black"  # Texto negro.
    )
    resultados_widget.configure(state="disabled")  # Inicialmente deshabilitado.
    resultados_widget.pack(pady=10)  # Empaquetado con margen vertical de 10 píxeles.



    # Etiqueta para mensajes temporales.
    mensaje_label = ctk.CTkLabel(
        parent,
        text="",  # Texto inicial vacío.
        font=("Arial", 13, "bold")  # Fuente Arial, tamaño 13, negrita.
    )
    mensaje_label.pack(pady=(2, 0))  # Margen vertical: 2 píxeles arriba, 0 abajo.

# ---------------------- FUNCIÓN PARA MOSTRAR MENSAJES TEMPORALES EN 'mensaje_label' ----------------------
    def mostrar_mensaje(texto, color):
        mensaje_label.configure(text=texto, text_color=color)  # Configura texto y color.
        parent.after(2500, lambda: mensaje_label.configure(text=""))  # Borra el texto tras 2.5 segundos.



# ---------------------- FUNCIÓN QUE ACTUALIZA EL PANEL CON LA LISTA DE ARCHIVOS ACTUALES ----------------------
    # Actualiza el panel con la lista de archivos actuales.
    def actualizar_panel_lista():
        resultados_widget.configure(state="normal")      # Habilita el texto.
        resultados_widget.delete("1.0", "end")           # Borra el contenido.
        for ruta in lista_archivos:
            resultados_widget.insert("end", f"{os.path.basename(ruta)}\n")  # Muestra solo el nombre del archivo.
        resultados_widget.configure(state="disabled")    # Vuelve a deshabilitar.



# ---------------------- FUNCIÓN PARA SELECCIONAR ARCHIVOS MEDIANTE UN CUADRO DE DIÁLOGO ----------------------
    def seleccionar_archivos():
        seleccionados = filedialog.askopenfilenames(  # Abre cuadro para elegir varios archivos.
            title="Seleccionar archivos",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if not seleccionados:  # Si no se selecciona nada, salir.
            return
        for ruta in seleccionados:
            if ruta not in lista_archivos:  # Evita duplicados.
                lista_archivos.append(ruta)

        # Habilita o deshabilita botones según si hay archivos cargados.
        boton_eliminar.configure(state="normal" if lista_archivos else "disabled")
        boton_revisar.configure(state="normal" if lista_archivos else "disabled")
        actualizar_panel_lista()



# ---------------------- FUNCIÓN PARA ELIMINAR ARCHIVOS SELECCIONADOS DE LA LISTA ----------------------
    def eliminar_archivos():
        if not resultados_widget.tag_ranges("sel"):  # Si no hay selección en el textbox...
            mostrar_mensaje("⚠ Debes seleccionar al menos un archivo", "yellow")
            return

        seleccion = resultados_widget.get("sel.first", "sel.last").strip().split("\n")  # Obtiene los nombres seleccionados.
        rutas_a_eliminar = [ruta for ruta in lista_archivos if os.path.basename(ruta) in seleccion]

        for ruta in rutas_a_eliminar:
            lista_archivos.remove(ruta)  # Elimina las rutas seleccionadas.

        boton_eliminar.configure(state="normal" if lista_archivos else "disabled")
        boton_revisar.configure(state="normal" if lista_archivos else "disabled")
        actualizar_panel_lista()

    # Configura etiquetas de color para el textbox (verde para éxito, rojo para error).
    resultados_widget.tag_config("exito", foreground="green")
    resultados_widget.tag_config("error", foreground="red") 



# ---------------------- FUNCIÓN PARA REVISAR LAS MARCAS DE LOS ARCHIVOS CARGADOS ----------------------
    def revisar_archivos():
        if not lista_archivos:  # Si la lista está vacía...
            mostrar_mensaje("⚠ No has seleccionado ningún archivo", "yellow")
            return

        resultados_widget.configure(state="normal")
        resultados_widget.delete("1.0", "end")  # Limpia el panel.

        for ruta in lista_archivos:
            nombre = os.path.basename(ruta)  # Nombre del archivo sin ruta.
            try:
                marca = extraer_marca_generica(ruta)  # Intenta extraer marca.
            except Exception as e:  # Si hay error al leer...
                resultados_widget.insert("end", f"❌ {nombre} → Error: {e}\n")
                continue
            if marca:
                resultados_widget.insert("end", f"✅ {nombre} → {marca}\n", "exito")
            else:
                resultados_widget.insert("end", f"❌ {nombre} → No se detectó marca este archivo\n", "error")
        resultados_widget.configure(state="disabled")



    # Botón para seleccionar archivos.
    boton_seleccionar = ctk.CTkButton(
        parent,
        text="Seleccionar archivos",  # Texto que muestra el botón.
        command=seleccionar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles
        height=50,  # Alto en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_seleccionar.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.



    # Botón para eliminar archivos seleccionados.
    boton_eliminar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Eliminar archivos seleccionados",  # Texto que muestra el botón.
        command=eliminar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles
        height=50,  # Alto en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        state="disabled"  # Inicialmente deshabilitado.
    )
    boton_eliminar.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.



    # Botón para revisar las marcas.
    boton_revisar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Revisar marcas",  # Texto que muestra el botón.
        command=revisar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles
        height=50,  # Alto en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        state="disabled"  # Inicialmente deshabilitado.
    )
    boton_revisar.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.



    # Botón para volver al menú principal.
    boton_volver = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Volver al menú principal",  # Texto que muestra el botón.
        command=volver_callback,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles
        height=50,  # Alto en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_volver.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.