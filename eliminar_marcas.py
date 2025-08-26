# Importa la biblioteca "customtkinter" y la renombra como "ctk"
# CustomTkinter es una versión mejorada de Tkinter con soporte para temas, colores y widgets modernos.
import customtkinter as ctk

# Importa desde tkinter el módulo "filedialog" para mostrar cuadros de diálogo
# que permiten seleccionar archivos o carpetas en el sistema operativo.
from tkinter import filedialog, messagebox

# Importa la biblioteca estándar "os" para trabajar con rutas, nombres de archivos, carpetas y funciones del sistema operativo.
import os


# ---------------------- CONSTANTES Y PARÁMETROS GLOBALES ----------------------
# Secuencia de bytes que indica el INICIO de una marca dentro del archivo (delimitador de apertura).
DELIM_INI = b"<<CTK_MARK_BEGIN>>"
# Secuencia de bytes que indica el FIN de una marca dentro del archivo (delimitador de cierre).
DELIM_FIN = b"<<CTK_MARK_END>>"
# Máximo de bytes a leer desde la cola (final) del archivo para buscar marcas (8 KB).
MAX_TAIL = 8192
# Proporción mínima (0.0–1.0) de caracteres imprimibles para considerar un texto "legible".
MIN_PRINTABLE_RATIO = 0.85



# -------- FUNCIÓN DE UTILIDADES DE DETECCIÓN (lectura y extracción de marca) --------
def _leer_tail(archivo, max_tail=MAX_TAIL):
    """
    Lee y devuelve como bytes la parte final de un archivo.
    - archivo: ruta al archivo a leer.
    - max_tail: cantidad máxima de bytes a leer desde el final (por defecto MAX_TAIL).
    """

    # Abre el archivo en modo binario de solo lectura ("rb").
    with open(archivo, "rb") as f:
        # Mueve el cursor de lectura al final del archivo.
        f.seek(0, os.SEEK_END)
        # Obtiene el tamaño total del archivo (en bytes).
        size = f.tell()

        # Si el tamaño supera el límite deseado...
        if size > max_tail:
            # ...posiciona el cursor "max_tail" bytes antes del final para leer solo la cola.
            f.seek(-max_tail, os.SEEK_END)
        else:
            # Si el archivo es pequeño, vuelve al inicio para leerlo completo.
            f.seek(0, os.SEEK_SET)
        # Lee desde la posición actual hasta el final y devuelve ese bloque (bytes).
        return f.read()




# ---------------------- FUNCIÓN QUE VERIFICA EL TEXTO ----------------------
def _es_printable_text(s: str) -> bool:
    """
    Determina si una cadena 's' contiene suficiente texto imprimible.
    - s: cadena a evaluar.
    Retorna True si la proporción de caracteres imprimibles >= MIN_PRINTABLE_RATIO.
    """

    # Si la cadena está vacía o None, no es válida.
    if not s:
        return False
    # Cuenta la cantidad de caracteres imprimibles usando str.isprintable().
    imprimibles = sum(ch.isprintable() for ch in s)
    # Calcula la relación imprimibles / longitud y la compara con el umbral.
    return (imprimibles / len(s)) >= MIN_PRINTABLE_RATIO


# ---------------------- FUNCIÓN QUE EXTRAE MARCAS CON DELIMITADORES ---------------------- 
def _extraer_por_delimitadores(datos_tail: bytes):
    """
    Intenta extraer una marca delimitada por [DELIM_INI ... DELIM_FIN] dentro de 'datos_tail'.
    - datos_tail: bytes leídos desde el final del archivo.
    Devuelve la marca decodificada (str) si se encuentra y es UTF-8 válido; si no, None.
    """
    
    # Busca la primera ocurrencia del delimitador de inicio en el bloque.
    ini = datos_tail.find(DELIM_INI)
    # Si no existe el inicio, no hay bloque delimitado.

    if ini == -1:
        return None
    # Avanza el índice para ubicarse justo después del delimitador de inicio.
    ini += len(DELIM_INI)
    # Busca el delimitador de fin a partir de 'ini' para cerrar el bloque.
    fin = datos_tail.find(DELIM_FIN, ini)

    # Si no existe el fin, el bloque está incompleto.
    if fin == -1:
        return None
    # Extrae los bytes comprendidos entre ambos delimitadores (excluyéndolos).
    bloque = datos_tail[ini:fin]
    try:
        # Intenta decodificar el bloque como UTF-8 estrictamente y elimina espacios extremos.
        texto = bloque.decode("utf-8", errors="strict").strip()
        # Devuelve el texto si no está vacío; si está vacío, devuelve None.
        return texto if texto else None
    except UnicodeDecodeError:
        # Si los bytes no son UTF-8 válido, no se considera una marca legible.
        return None



# ---------------------- FUNCIÓN QUE EXTRAE MARCAS MEDIANTE HEURÍSTICA ----------------------
def _extraer_por_heuristica(datos_tail: bytes):
    """
    Intenta extraer una marca sin delimitadores mediante heurística:
    - Usa la última (o penúltima) línea con suficiente texto "imprimible".
    - Si falla, toma la secuencia final de caracteres imprimibles recorriendo al revés.
    """

    # Si no hay datos, no se puede detectar nada.
    if not datos_tail:
        return None
    # Decodifica ignorando errores para conservar la mayor parte legible del texto.
    texto_tail = datos_tail.decode("utf-8", errors="ignore")

    # Si tras decodificar no hay nada, aborta.
    if not texto_tail:
        return None

    # ---- Heurística basada en líneas ----
    # Divide por líneas para evaluar la última o penúltima como posible marca.
    partes = texto_tail.splitlines()
    if partes:
        # Toma la última línea; si está vacía, intenta con la penúltima (si existe).
        candidato = partes[-1].strip() or (partes[-2].strip() if len(partes) >= 2 else "")
        # Si hay candidato y cumple con el umbral de texto imprimible, devuélvelo.
        if candidato and _es_printable_text(candidato):
            return candidato

    # ---- Heurística basada en caracteres finales ----
    # Recorre el texto al revés acumulando solo caracteres imprimibles hasta encontrar uno no imprimible.
    acumulado = []
    for ch in reversed(texto_tail):
        # Si el carácter es imprimible, lo acumula.
        if ch.isprintable():
            acumulado.append(ch)
        else:
            # Al encontrar uno no imprimible, corta la acumulación.
            break

    # Si se acumularon caracteres...
    if acumulado:
        # Reconstruye el texto en el orden correcto y quita espacios extremos.
        candidato = "".join(reversed(acumulado)).strip()
        # Verifica que sea texto suficientemente imprimible y devuélvelo.
        if candidato and _es_printable_text(candidato):
            return candidato
    # Si ninguna heurística encontró marca legible, devuelve None.
    return None



# ---------------------- FUNCIÓN QUE EXTRAE MARCAS GENÉRICA ----------------------
def extraer_marca_generica(archivo):
    """
    Extrae una marca genérica de 'archivo':
    - Primero intenta por delimitadores.
    - Si no hay delimitadores válidos, usa la heurística.
    Devuelve la marca como str o None si no se detecta.
    """

    # Lee la sección final del archivo respetando el tope MAX_TAIL.
    tail = _leer_tail(archivo, MAX_TAIL)
    # Intenta extraer marcas claramente delimitadas.
    marca = _extraer_por_delimitadores(tail)
    # Si hubo éxito con delimitadores, retorna esa marca; si no, cae a la heurística.
    return marca if marca else _extraer_por_heuristica(tail)



# ---------------------- FUNCIÓN DE ELIMINACIÓN SEGURA DE MARCAS (modifica el archivo si encuentra marca) ----------------------
def _borrar_marca(archivo) -> bool:
    """
    Intenta borrar la marca del archivo 'archivo' usando dos estrategias:
      1) Si existen delimitadores [DELIM_INI ... DELIM_FIN], elimina ese bloque completo.
      2) Si no hay delimitadores, intenta eliminar la cola si coincide con una marca detectada
         (contemplando variantes con saltos de línea \n y \r\n).
    Retorna:
      - True si el archivo fue modificado.
      - False si no se detectó/quitó ninguna marca.
    """

    # Abre y lee el archivo completo en memoria como bytes (necesario para manipular cortes).
    with open(archivo, "rb") as f:
        data = f.read()

    # ---------------------- MÉTODO 1: por delimitadores ----------------------
    # Busca la ÚLTIMA aparición del delimitador de inicio (rfind por si hubiera más de un bloque).
    ini = data.rfind(DELIM_INI)

    # Si existe un inicio potencial de bloque...
    if ini != -1:
        # Busca el delimitador de fin a partir del final del inicio encontrado.
        fin = data.find(DELIM_FIN, ini + len(DELIM_INI))

        # Si también existe fin...
        if fin != -1:
            # Ajusta 'fin' para incluir el propio delimitador de cierre en el borrado.
            fin += len(DELIM_FIN)
            # Construye los nuevos bytes del archivo saltando el bloque [ini:fin].
            nuevo = data[:ini] + data[fin:]
            # Reescribe el archivo completo sin el bloque de marca.
            with open(archivo, "wb") as f:
                f.write(nuevo)
            # Indica que se modificó.
            return True

    # ---------------------- MÉTODO 2: heurística (marca al final) ----------------------
    # Intenta detectar una marca "legible" (sin delimitadores).
    marca = extraer_marca_generica(archivo)

    # Si existe una posible marca...
    if marca:
        # Codifica la marca a bytes UTF-8 para poder compararla con 'data'.
        m = marca.encode("utf-8", "ignore")
        # Prepara variantes de sufijo que podrían estar al final del archivo (Unix \n, Windows \r\n, sin salto).
        candidatos = [m, b"\n" + m, m + b"\n", b"\r\n" + m, m + b"\r\n"]
        # Recorre cada posible sufijo...
        for suf in candidatos:

            # Si el archivo termina exactamente con ese sufijo...
            if data.endswith(suf):
                # Calcula el nuevo contenido quitando la longitud del sufijo desde el final.
                nuevo = data[: len(data) - len(suf)]
                # Reescribe el archivo sin esa cola que corresponde a la marca.
                with open(archivo, "wb") as f:
                    f.write(nuevo)
                # Indica que se modificó.
                return True

    # Si no se encontró o no se pudo eliminar nada, devuelve False.
    return False


# ---------------------- FUNCIÓN DE LA PANTALLA DE ELIMINAR MARCAS (integrable en principal.py) ----------------------
def mostrar_eliminar_marcas(parent, volver_callback, boton_font):
    """
    Construye y muestra la pantalla para eliminar marcas dentro del contenedor 'parent'.
    Parámetros:
      - parent: widget contenedor (ej. un Frame o ventana) donde se montará la UI.
      - volver_callback: función a ejecutar al presionar el botón "Volver".
      - boton_font: objeto/fuente a usar en los botones (familia, tamaño, peso).
    """

    # Limpia el contenedor: oculta cualquier widget que ya estuviera empaquetado dentro de 'parent'.
    for widget in parent.winfo_children():
        widget.pack_forget()




    # ---------------------- TÍTULO ----------------------
    # Crea una etiqueta (Label) con el título de la pantalla.
    titulo = ctk.CTkLabel(
        parent,  # Contenedor padre donde se colocará el título.
        text="Eliminar Marcas",  # Texto visible del título.
        font=("Arial", 22, "bold")  # Fuente: tamaño 22, negrita ("bold").
    )
    # Empaqueta (muestra) el título con un margen vertical de 20 píxeles arriba y abajo.
    titulo.pack(pady=12)


    # ---------------------- LISTA DE ARCHIVOS SELECCIONADOS ----------------------
    # Lista de tuplas (ruta, marca) que representan los archivos detectados con su marca legible.
    lista_archivos = []


    # ---------------------- PANEL DE RESULTADOS ----------------------
    # Crea un cuadro de texto para listar archivos y sus marcas detectadas.
    panel = ctk.CTkTextbox(
        parent,  # Contenedor principal.
        width=520,  # Ancho de 500 píxeles.
        height=260,  # Alto de 200 píxeles.
        fg_color="white",  # Color de fondo (blanco).
        text_color="black"  # Color del texto (negro).
    )
    # Inhabilita la edición del panel para que sea solo lectura inicialmente.
    panel.configure(state="disabled")
    # Empaqueta el panel con padding vertical de 8 píxeles.
    panel.pack(pady=8)

    # Define una etiqueta ("tag") de formato llamada "ok" con color verde para el ícono de éxito.
    panel.tag_config("ok", foreground="green")



    # ---------------------- MENSAJES ----------------------
    # Crea una etiqueta para mostrar mensajes temporales (advertencias, confirmaciones, errores).
    mensaje_label = ctk.CTkLabel(
        parent,  # Contenedor principal.
        text="",  # Empieza vacío.
        font=("Arial", 14, "bold")  # Fuente Arial, tamaño 14, en negrita.
    )
    # Muestra la etiqueta con un margen superior de 5 píxeles y sin margen inferior.
    mensaje_label.pack(pady=(2, 0))



    # ---------------------- FUNCIÓN PARA MOSTRAR MENSAJES ----------------------
    def mostrar_mensaje(texto, color):
        """
        Muestra un mensaje en "mensaje_label" con un color específico y lo borra después de 3,5 segundos.
        """

        # Cambia el texto y el color de la etiqueta.
        mensaje_label.configure(text=texto, text_color=color)
        # Usa "after" para ejecutar una función después de 3300 ms (3,3 segundos).
        # Aquí se usa para vaciar el texto después del tiempo.
        parent.after(3300, lambda: mensaje_label.configure(text=""))



    # ---------------------- FUNCIÓN PARA ACTUALIZAR LISTA ----------------------
    def mostrar_lista():
        """
        Refresca el 'panel' con los elementos de 'lista_archivos'.
        Muestra: '✅ <nombre_archivo> → <marca_detectada>'
        """
        
        # Activa la edición temporalmente para poder modificar el contenido.
        panel.configure(state="normal")
        # Borra todo lo que había antes en el panel.
        panel.delete("1.0", "end")

        # Recorre cada par (ruta, marca) y lo inserta línea a línea.
        for ruta, marca in lista_archivos:
            # Inserta el ícono de check con la tag "ok" para que salga en verde.
            panel.insert("end", "✅ ", "ok")
            # Inserta el nombre base del archivo (sin ruta) y la marca asociada.
            panel.insert("end", f"{os.path.basename(ruta)} → {marca}\n")
        # Vuelve a poner el panel en modo solo lectura para evitar ediciones del usuario.
        panel.configure(state="disabled")
        # Habilita o deshabilita el botón de eliminar según haya o no elementos listados.
        boton_eliminar.configure(state="normal" if lista_archivos else "disabled")



    # ---------------------- FUNCIÓN PARA ACTUALIZAR LISTA ----------------------
    def seleccionar_archivos():
        """
        Abre un cuadro de diálogo para seleccionar uno o más archivos.
        - Detecta marcas en cada archivo seleccionado y llena 'lista_archivos' con (ruta, marca).
        - Muestra advertencia si no se detectó ninguna marca.
        """
        # Muestra el diálogo del sistema para seleccionar archivos múltiples.
        rutas = filedialog.askopenfilenames(
            title="⚠ Debes seleccionar al menos un archivo", # Título del diálogo (mensaje al usuario).
            filetypes=[("Todos los archivos", "*.*")]         # Filtro: permitir cualquier extensión.
        )
        # Si el usuario canceló o no eligió nada, finaliza sin cambios.
        if not rutas:
            return

        # Limpia la lista previa para evitar duplicados/estado residual.
        lista_archivos.clear()
        # Recorre cada ruta seleccionada por el usuario.
        for ruta in rutas:
            try:
                # Intenta extraer una marca legible del archivo.
                marca = extraer_marca_generica(ruta)
                # Si se obtuvo alguna marca, añade el par (ruta, marca) a la lista.
                if marca:
                    lista_archivos.append((ruta, marca))
            except Exception:
                # Si ocurre un error con un archivo (permisos, codificación, etc.), lo omite.
                pass

        # Actualiza el panel con el resultado de la detección.
        mostrar_lista()
        # Si la lista quedó vacía, informa que no se detectaron marcas en los seleccionados.
        if not lista_archivos:
            mostrar_mensaje("No se detectaron marcas en los archivos seleccionados.", "yellow")



    # ---------------------- FUNCIÓN PARA ELIMINAR MARCAS ----------------------
    def eliminar_marcas():
        """
        Elimina las marcas de todos los archivos actualmente listados en 'lista_archivos'.
        - Pide confirmación al usuario antes de modificar archivos.
        - Tras completar, limpia el panel y deshabilita el botón de eliminar.
        """

        # Si no hay elementos en la lista, no hay nada que hacer.
        if not lista_archivos:
            return
        
        # Ventana de confirmación (sí/no) para evitar modificaciones accidentales.
        if not messagebox.askyesno("Confirmar eliminación", "¿Eliminar las marcas de los archivos listados?"):
            return

        # Contador de archivos modificados (informativo; aquí no se muestra, pero es útil si quisieras loguear).
        modificados = 0
        # Recorre cada archivo (la marca no se usa en esta función; por eso se ignora con '_').
        for ruta, _ in lista_archivos:
            try:
                # Intenta borrar la marca del archivo; si logra modificar, incrementa el contador.
                if _borrar_marca(ruta):
                    modificados += 1
            except Exception as e:
                # Si algo falla, imprime el error en consola (no rompe la ejecución del resto).
                print(f"Error al limpiar {ruta}: {e}")

        # Informa al usuario que la operación finalizó correctamente con un cuadro de diálogo informativo.
        messagebox.showinfo("Operación completada", "La operación se realizó exitosamente.")
        # ---- Reset visual y de estado ----
        # Vacía la lista interna para reflejar que ya no hay pendientes.
        lista_archivos.clear()
        # Habilita el panel para poder limpiarlo.
        panel.configure(state="normal")
        # Elimina todo el texto del panel.
        panel.delete("1.0", "end")
        # Devuelve el panel a modo solo lectura.
        panel.configure(state="disabled")
        # Deshabilita el botón de eliminar hasta que se vuelvan a seleccionar archivos.
        boton_eliminar.configure(state="disabled")



    # ---------------------- BOTÓN PARA SELECCIONAR ARCHIVOS ----------------------
    boton_seleccionar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Seleccionar archivos",  # Texto que muestra el botón.
        command=seleccionar_archivos,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_seleccionar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.



    # ---------------------- BOTÓN PARA ELIMINAR MARCAS ----------------------
    boton_eliminar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Eliminar marcas",  # Texto que muestra el botón.
        command=eliminar_marcas,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        state="disabled",  # # Comienza deshabilitado hasta que haya archivos en la lista.
    )
    boton_eliminar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.



    # ---------------------- BOTÓN PARA VOLVER AL MENÚ PRINCIPAL ----------------------
    boton_volver = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Volver al menú principal",  # Texto que muestra el botón.
        command=volver_callback,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font,  # Fuente usada para el texto.
    )
    boton_eliminar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.