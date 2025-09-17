# Importa la biblioteca "customtkinter" y la renombra como "ctk"
# CustomTkinter es una versión mejorada de Tkinter con soporte para temas, colores y widgets modernos.
import customtkinter as ctk

# Importa tkinter como tk: se utiliza para widgets básicos que no provee ctk
# o para funciones específicas (ej. Entry colocado manualmente sobre un Treeview).
import tkinter as tk

# Importamos la librería PIL (Python Imaging Library) para abrir imágenes.
from PIL import Image

# Importa ttk desde tkinter: contiene widgets temáticos como Treeview (tablas), Style, etc.
from tkinter import ttk

"""
Importa el módulo json para serializar y deserializar estructuras de Python (listas/diccionarios)
al formato JSON y viceversa. Se usa para guardar/cargar usuarios en disco.
"""
import json

# Importa la biblioteca estándar "os" para trabajar con rutas, nombres de archivos, carpetas y funciones del sistema operativo.
import os

from administrar_pagos import mostrar_administrar_pagos


# Nombre del archivo donde se guardan los datos de usuarios en formato JSON.
USUARIOS_FILE = "usuarios.json"



# ---------------------- MANEJO DE DATOS ----------------------
def cargar_usuarios():
    """
    Lee y devuelve la lista de usuarios guardada en USUARIOS_FILE.
    - Si el archivo existe: lo abre en modo lectura y devuelve el JSON parseado (lista/dict).
    - Si no existe: devuelve una lista vacía para evitar errores al iterar.
    """

    # Comprueba si el archivo físico existe en el disco.
    if os.path.exists(USUARIOS_FILE):
        # Abre el archivo en modo lectura con codificación UTF-8.
        with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
            # Parsea el contenido JSON y lo devuelve como objeto Python (lista de dicts).
            return json.load(f)
    # Si no existe, retorna lista vacía (no hay usuarios guardados aún).
    return []


def guardar_usuarios(usuarios):
    """
    Guarda la lista de usuarios pasada como argumento en el archivo USUARIOS_FILE.
    - Usa json.dump con indentado para que el archivo sea legible.
    - ensure_ascii=False para preservar acentos y caracteres Unicode.
    """

    # Abre (o crea) el archivo en modo escritura, truncando su contenido previo.
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        # Serializa la lista/dict de usuarios a JSON y lo escribe en disco.
        json.dump(usuarios, f, indent=4, ensure_ascii=False)



# ---------------------- FUNCIÓN PARA MOSTRAR PANTALLA DE REGISTRO ----------------------
def mostrar_patreon_drago(parent, volver_callback, boton_font):
    """
    Construye y muestra la interfaz para administrar registros (crear/editar/eliminar/copiar).
    Parámetros:
    - parent: widget contenedor (p. ej. un Frame o la ventana principal) donde se cargan todos los widgets.
    - volver_callback: función a ejecutar cuando el usuario presiona el botón de volver.
    - boton_font: tupla/fuente que se usará para los botones (consistencia visual).
    """

    # ---------------------- LIMPIAR PANTALLA ----------------------
    # Elimina/oculta cualquier widget que estuviese en el contenedor parent para pintar la pantalla nueva.
    for widget in parent.winfo_children():
        widget.pack_forget()

    # Carga los usuarios existentes desde el archivo JSON (si existe).
    usuarios = cargar_usuarios()

    # ---------------------- TÍTULO ----------------------
    # Crea una etiqueta (label) grande con el título de la pantalla.
    titulo = ctk.CTkLabel(
        parent,  # Contenedor donde se coloca el texto.
        text="Patreon Drago",  # Texto que se muestra.
        font=("Arial", 22, "bold")  # Fuente: tamaño 22, negrita ("bold").
    )
    # Empaqueta (muestra) el título con margen vertical.
    titulo.pack(pady=12)



    # ---------------------- BARRA DE BÚSQUEDA ----------------------
    # Frame que contendrá la etiqueta "Buscar" y el Entry para filtrar la tabla.
    frame_busqueda = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )
    frame_busqueda.pack(fill="x", padx=12, pady=(5, 5))

    # Etiqueta que indica la función del campo (añade un emoji lupa para claridad).
    lbl_buscar = ctk.CTkLabel(
        frame_busqueda,  # Contenedor principal.
        text="Buscar:",  # Texto que muestra el botón.
        font=("Arial", 14)  # Fuente y tamaño del texto.
    )
    lbl_buscar.pack(side="left", padx=(0, 8))  # Coloca la etiqueta a la izquierda con 8px de espacio a la derecha.

    # Entry (campo de texto) con placeholder para que el usuario escriba su búsqueda.
    entry_buscar = ctk.CTkEntry(
        frame_busqueda, # Contenedor principal.
        placeholder_text="Escribe para filtrar..."  # Texto que muestra el botón.
    )
    # Se empaqueta y se le permite expandir horizontalmente para ocupar el ancho restante.
    entry_buscar.pack(side="left", fill="x", expand=True, padx=5)

    # Función que filtra la tabla en tiempo real usando el contenido del Entry.
    def filtrar_tabla(event=None):
        # Obtiene la query en minúsculas para comparaciones case-insensitive.
        query = entry_buscar.get().lower()
        # Borra todas las filas visibles de la tabla antes de volver a insertar las que coinciden.
        tabla.delete(*tabla.get_children())  # limpiar tabla

        # Recorre cada usuario cargado de disco y verifica si alguno de sus campos
        # contiene el texto buscado.
        for usuario in usuarios:
            # Convierte los valores del dict a lista para poder buscar en cualquiera de ellos.
            valores = list(usuario.values())
            # any(...) devuelve True si la query aparece en alguno de los campos.
            if any(query in str(v).lower() for v in valores):
                # Si coincide, se inserta la fila con los valores tal cual están.
                tabla.insert("", "end", values=tuple(valores))

    # Vincula la función al evento KeyRelease del Entry para filtrar mientras se escribe.
    entry_buscar.bind("<KeyRelease>", filtrar_tabla)



    # ---------------------- BOTONES ----------------------
    # Frame contenedor para los botones de acción (Agregar/Editar/Eliminar/Guardar).
    frame_botones = ctk.CTkFrame(
        parent,  # Contenedor principal.
        fg_color="transparent"  # Fondo transparente para integrarse con el diseño.
    )
    frame_botones.pack(fill="x", pady=(0, 5))  # Ocupa todo el ancho y agrega 5px de espacio abajo.

    # Diccionario que mantiene el estado de la pantalla:
    # - modo: "agregar", "editar" o None
    # - fila_agregada: id de la fila recién creada (si se está agregando)
    # - entry_activo: referencia al Entry creado para editar una celda (para poder destruirlo luego)
    estado_accion = {"modo": None, "fila_agregada": None, "entry_activo": None}



    # ---------------------- FUNCIONES DE LOS BOTONES ----------------------
    def agregar_usuario():
        """
        Crea una fila vacía al final de la tabla para que el usuario ingrese los datos.
        Establece el estado en modo 'agregar' para permitir edición solo en esa fila.
        """

        # Cambia el modo a 'agregar'.
        estado_accion["modo"] = "agregar"
        # Inserta una fila con valores vacíos (una columna por cada campo definido en 'columnas').
        fila_id = tabla.insert("", "end", values=("", "", "", "", "", "", "", "", ""))
        # Guarda el id de la fila creada para que solo esa fila sea editable en modo agregar.
        estado_accion["fila_agregada"] = fila_id  # Guardamos la fila nueva
        # Selecciona automáticamente la fila creada para dar feedback visual.
        tabla.selection_set(fila_id)
        # Muestra mensaje informativo al usuario.
        mostrar_mensaje("➕ Fila creada, completa los datos y luego usa 'Guardar cambios'", "cyan")


    def editar_usuario():
        """
        Cambia el modo a 'editar' (permite editar cualquier fila seleccionada).
        Si no hay selección, muestra advertencia.
        """
        seleccion = tabla.selection()
        if not seleccion:
            mostrar_mensaje("⚠ Selecciona un usuario para editar", "yellow")
            return
        # Cambia el modo a editar y resetea la referencia a fila agregada.
        estado_accion["modo"] = "editar"
        estado_accion["fila_agregada"] = None
        mostrar_mensaje("✏ Edita los campos con doble clic, luego presiona 'Guardar cambios'", "cyan")


    def eliminar_usuario():
        """
        Elimina las filas seleccionadas tanto de la vista (Treeview) como del archivo de datos.
        Actualiza el archivo JSON llamando a guardar_usuarios.
        """

        seleccion = tabla.selection()
        if not seleccion:
            mostrar_mensaje("⚠ Selecciona al menos un usuario", "yellow")
            return

        # Recorre cada item seleccionado y lo elimina.
        for item in seleccion:
            # Obtiene el índice (posición) de la fila dentro del Treeview.
            idx = tabla.index(item)
            # Elimina visualmente la fila del Treeview.
            tabla.delete(item)
            # Elimina la entrada correspondiente en la lista 'usuarios' cargada en memoria.
            # IMPORTANTE: Debes usar pop(idx) asume que el orden en la tabla corresponde al orden en la lista.
            usuarios.pop(idx)
        # Guarda los cambios en disco.
        guardar_usuarios(usuarios)
        mostrar_mensaje("🗑 Usuario(s) eliminado(s)", "red")
        # Resetea el estado de acción.
        estado_accion["modo"] = None
        estado_accion["fila_agregada"] = None


    def guardar_cambios():
        """
        Guarda la fila actualmente seleccionada en la lista 'usuarios' y en el archivo JSON.
        Soporta tanto la actualización de una fila existente como la inserción de una nueva.
        """

        seleccion = tabla.selection()
        if not seleccion:
            mostrar_mensaje("⚠ No hay ninguna fila seleccionada", "yellow")
            return

        # Toma el primer elemento seleccionado (soporta múltiples, pero guarda el primero).
        item_id = seleccion[0]
        # Recupera los valores visibles de la fila (tuple de strings).
        valores = tabla.item(item_id, "values")

        # Si la fila está vacía (todos los campos vacíos), muestra advertencia.
        if not any(valores):
            mostrar_mensaje("⚠ Completa al menos un campo", "yellow")
            return

        # Calcula el índice numérico de la fila en la tabla.
        fila_idx = tabla.index(item_id)

        # Si el índice existe dentro de la lista 'usuarios', actualiza el registro correspondiente.
        if fila_idx < len(usuarios):
            usuarios[fila_idx] = dict(zip(columnas, valores))
        else:
            # Si el índice está fuera del rango, se asume que es una nueva fila y se agrega.
            usuarios.append(dict(zip(columnas, valores)))

        # Persiste los cambios en disco.
        guardar_usuarios(usuarios)
        mostrar_mensaje("✔ Cambios guardados", "green")


        # ---------------------- CERRAR CUALQUIER ENTRY ABIERTO ----------------------
        # Si existe un Entry creado para editar una celda, intentamos destruirlo para limpiar la UI.
        if estado_accion["entry_activo"] is not None:
            try:
                estado_accion["entry_activo"].destroy()
            except:
                # En caso de error ignoramos para no romper la interfaz (defensa suave).
                pass
            estado_accion["entry_activo"] = None


        # ---------------------- RESET ESTADO ----------------------
        estado_accion["modo"] = None
        estado_accion["fila_agregada"] = None
        # Quita la selección de la tabla.
        tabla.selection_remove(item_id)



    # ---------------------- CARGA DE LOS ICONOS DE LOS BOTONES ----------------------
    """
    Este es el icono para el botón agregar.
    Se abre la imagen "agregar_usuario.png" desde la ruta indicada y se 
    convierte a un objeto CTkImage y se ajusta a 25x25 píxeles.
    """
    icono_agregar = ctk.CTkImage(
        Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\agregar_usuario.png"), 
        size=(25, 25)  
    )

    """
    Este es el icono para el botón editar.
    Se abre la imagen "editar_usuario.png" desde la ruta indicada y se 
    convierte a un objeto CTkImage y se ajusta a 25x25 píxeles.
    """
    icono_editar = ctk.CTkImage(
        Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\editar_usuario.png"),
        size=(25, 25)
    )

    """
    Este es el icono para el botón eliminar.
    Se abre la imagen "eliminar_usuario.png" desde la ruta indicada y se 
    convierte a un objeto CTkImage y se ajusta a 25x25 píxeles.
    """
    icono_eliminar = ctk.CTkImage(
        Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\eliminar_usuario.png"),
        size=(25, 25)
    )

    """
    Este es el icono para el botón guardar.
    Se abre la imagen "guardar_cambios.png" desde la ruta indicada y se 
    convierte a un objeto CTkImage y se ajusta a 25x25 píxeles.
    """
    icono_guardar = ctk.CTkImage(
        Image.open(r"C:\Users\LENOVO\Desktop\DragoCrypt\img\guardar_cambios.png"),
        size=(25, 25)
    )



    # ---------------------- BOTÓN PARA AGREGAR USUARIOS ----------------------
    boton_agregar = ctk.CTkButton(
        frame_botones,  # Contenedor principal.
        text="Agregar",  # Texto que muestra el botón.
        image=icono_agregar,  # Icono que muestra el botón.
        command=agregar_usuario,  # Función que se ejecuta al hacer clic.
        width=120,  # Ancho del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_agregar.pack(side="left", padx=5)  # Coloca el botón en el contenedor, alineado a la izquierda con 5px de espacio horizontal.



    # ---------------------- BOTÓN PARA EDITAR USUARIOS ----------------------
    boton_editar = ctk.CTkButton(
        frame_botones,  # Contenedor principal.
        text="Editar",  # Texto que muestra el botón.
        image=icono_editar,  # Icono que muestra el botón.
        command=editar_usuario,  # Función que se ejecuta al hacer clic.
        width=120,  # Ancho del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_editar.pack(side="left", padx=5)  # Coloca el botón en el contenedor, alineado a la izquierda con 5px de espacio horizontal.

    
    
    # ---------------------- BOTÓN PARA ELIMINAR USUARIOS ----------------------
    boton_eliminar = ctk.CTkButton(
        frame_botones,  # Contenedor principal.
        text="Eliminar",  # Texto que muestra el botón.
        image=icono_eliminar,  # Icono que muestra el botón.
        command=eliminar_usuario,  # Función que se ejecuta al hacer clic.
        width=120,  # Ancho del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_eliminar.pack(side="left", padx=5)  # Coloca el botón en el contenedor, alineado a la izquierda con 5px de espacio horizontal.

    
    
    # ---------------------- BOTÓN PARA GUARDAR CAMBIOS ----------------------
    boton_guardar = ctk.CTkButton(
        frame_botones,  # Contenedor principal.
        text="Guardar",  # Texto que muestra el botón.
        image=icono_guardar,  # Icono que muestra el botón.
        command=guardar_cambios,  # Función que se ejecuta al hacer clic.
        width=120,  # Ancho del botón en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_guardar.pack(side="right", padx=5)  # Coloca el botón en el contenedor, alineado a la izquierda con 5px de espacio horizontal.



    # ---------------------- FRAME TABLA ----------------------
    # Frame contenedor donde se colocará la tabla (Treeview) y sus scrollbars.
    frame_tabla = ctk.CTkFrame(
        parent,
        fg_color="#212121", 
        corner_radius=10
    )
    frame_tabla.pack(fill="both", expand=True, padx=12, pady=8)

    # Scrollbar vertical (barra lateral) para desplazar filas.
    scrollbar_y = ctk.CTkScrollbar(
        frame_tabla, 
        orientation="vertical"
    )
    scrollbar_y.pack(side="right", fill="y")

    # Scrollbar horizontal para desplazar columnas si exceden el ancho.
    scrollbar_x = ctk.CTkScrollbar(
        frame_tabla,
        orientation="horizontal"
    )
    scrollbar_x.pack(side="bottom", fill="x")


    # ---------------------- TREEVIEW (TABLA) ----------------------
    # Configuración de estilo para el Treeview usando ttk.Style().
    style = ttk.Style()
    # Selecciona el tema 'clam' (neutro y que permite configuraciones de color).
    style.theme_use("clam")
    # Define aspectos visuales de la tabla: fondo, color de texto, altura de fila, etc.
    style.configure(
        "Custom.Treeview", # Nombre del estilo que luego se asignará al Treeview.
        background="#000000", # Color de fondo de las filas (negro absoluto, para dar contraste).
        foreground="white", # Color del texto dentro de cada celda de la tabla (blanco sobre negro para máxima legibilidad).
        rowheight=30, # Altura de cada fila de la tabla (30 píxeles, para que los registros tengan más espacio y se vean claros).
        fieldbackground="#0A0A0A", # Color de fondo alternativo o del área de la tabla (un negro un poco más claro que el fondo principal, para dar leve contraste).
        font=("Arial", 11) # Fuente y tamaño del texto dentro del Treeview (Arial, tamaño 11, sencillo y legible).
    )
    
    # Define mapa de estilos para el estado 'selected' (cuando una fila está seleccionada).
    style.map("Custom.Treeview",
              background=[("selected", "#00D3C1")],  #Color de fondo de la fila cuando está seleccionada.
              foreground=[("selected", "white")])  #Color del texto de la fila seleccionada (blanco en este caso).
    
    # Configura también los encabezados de la tabla.
    style.configure(
        "Custom.Treeview.Heading",  # Estilo aplicado a los encabezados (las cabeceras de las columnas)
        background="#000000",  # Fondo de los encabezados en color negro.
        foreground="white",  # Texto de los encabezados en color blanco.
        font=("Arial", 12, "bold")  # Fuente de los encabezados: Arial, tamaño 12, en negrita.
    )


    # ---------------------- DEFINICIÓN DE COLUMNAS ----------------------
    # Tupla con los nombres de columnas que representarán cada campo del usuario.
    columnas = (
        "Nombre",
        "Apellido",
        "País",
        "Email",
        "Instagram", 
        "Discord", 
        "Usuario Telegram",
        "ID Telegram"
    )

    """ 
    Crea el Treeview con las columnas definidas. show="headings" oculta la primera columna
    que normalmente se usa como índice, mostrando sólo las cabeceras que definimos.
    """
    tabla = ttk.Treeview(
        frame_tabla, 
        columns=columnas,
        show="headings",
        height=12, 
        style="Custom.Treeview"
    )
    tabla.pack(fill="both", expand=True, padx=5, pady=5)

    # Vincula las barras de desplazamiento con la vista de la tabla para que actúen correctamente.
    tabla.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    scrollbar_y.configure(command=tabla.yview)
    scrollbar_x.configure(command=tabla.xview)

    # Configura encabezados y ancho/alineación de cada columna.
    for col in columnas:
        tabla.heading(col, text=col)  # Texto del encabezado
        tabla.column(col, width=140, anchor="center")  # Ancho fijo y texto centrado



    # ---------------------- CARGAR DATOS INICIALES ----------------------
    # Inserta en la tabla los usuarios cargados desde el archivo JSON.

    for usuario in usuarios:
        # Crea una tupla con el valor de cada columna (si falta, usa cadena vacía).
        valores = tuple(usuario.get(col, "") for col in columnas)
        tabla.insert("", "end", values=valores)



    # ---------------------- FUNCIÓN PARA EDITAR CELDAS ----------------------
    def editar_celda(event):
        """
        Permite editar el contenido de una celda creando temporalmente un Entry sobre la celda.
        - Solo funciona si el modo actual es 'agregar' o 'editar'.
        - En modo 'agregar' sólo la fila recién creada (fila_agregada) puede editarse.
        """

        # Si no estamos en modo agregar o editar, no permitimos el acceso a edición directa.
        if estado_accion["modo"] not in ("agregar", "editar"):
            return

        # Identifica la fila y la columna donde ocurrió el evento (posición y coordenadas).
        item_id = tabla.identify_row(event.y)
        col = tabla.identify_column(event.x)
        # Si no hay fila o columna identificada, salir (click fuera de áreas válidas).
        if not item_id or not col:
            return

        # En modo agregar, sólo permitimos editar la fila que se acaba de crear.
        if estado_accion["modo"] == "agregar" and item_id != estado_accion["fila_agregada"]:
            mostrar_mensaje("⚠ Solo puedes editar la fila que acabas de agregar", "yellow")
            return

        # Calcula el índice de columna (col viene como "#1", "#2", ...)
        col_idx = int(col.replace("#", "")) - 1
        # Recupera la lista de valores actuales de la fila (mutable para actualizar).
        valores = list(tabla.item(item_id, "values"))
        # Obtiene la posición y tamaño (x,y,width,height) de la celda para colocar el Entry encima.
        x, y, width, height = tabla.bbox(item_id, col)
        # Crea un Entry normal de tkinter (no CTk) y lo posiciona exactamente en la celda.
        entry = tk.Entry(tabla)
        entry.place(x=x, y=y, width=width, height=height)
        # Inserta el valor actual de la celda en el Entry para que el usuario lo edite.
        entry.insert(0, valores[col_idx])
        # Da foco para que el usuario pueda escribir directamente.
        entry.focus()
        # Guarda referencia al Entry activo en estado_accion para poder destruirlo más tarde si es necesario.
        estado_accion["entry_activo"] = entry  # Guardamos referencia



        # ---------------------- FUNCIÓN PARA GUARDAR VALORES ----------------------
        def guardar_valor(event=None):
            # Función local para guardar el valor al pulsar Enter o al perder foco.

            # Actualiza la lista de valores con el contenido del Entry.
            valores[col_idx] = entry.get()
            # Actualiza la fila en el Treeview con los nuevos valores.
            tabla.item(item_id, values=valores)
            # Destruye el Entry y resetea la referencia activa.
            entry.destroy()
            estado_accion["entry_activo"] = None
        # Vincula Enter y FocusOut al guardado automático.
        entry.bind("<Return>", guardar_valor)
        entry.bind("<FocusOut>", guardar_valor)
        # Evento: doble clic izquierdo en una celda inicia la edición.
    tabla.bind("<Double-1>", editar_celda)



    # ---------------------- FUNCIÓN PARA COPIAR FILAS ----------------------
    def copiar_fila(event=None):
        """
        Copia el contenido textual de las filas seleccionadas al portapapeles.
        - Las columnas vacías se omiten en la representación textual.
        - Cada fila se separa por una nueva línea cuando se copian múltiples.
        """

        seleccion = tabla.selection()
        if not seleccion:
            mostrar_mensaje("⚠ Selecciona una o varias filas para copiar", "yellow")
            return

        lineas = []
        # Recorre las filas seleccionadas y construye una lista de strings por fila.
        for item_id in seleccion:
            valores = tabla.item(item_id, "values")
            # Une los valores no vacíos con " - " para formar una sola línea por fila.
            texto = " - ".join([str(v) for v in valores if v])  # unir solo si no está vacío
            if texto.strip():
                lineas.append(texto)

        if lineas:
            # Junta todas las líneas en un texto final separado por saltos de línea.
            texto_copiado = "\n".join(lineas)  # cada fila en una línea nueva
            # Limpia el portapapeles del parent y copia el texto generado.
            parent.clipboard_clear()
            parent.clipboard_append(texto_copiado)
            parent.update()  # Necesario para mantenerlo en el portapapeles
            mostrar_mensaje("📋 Filas copiadas al portapapeles", "green")
        else:
            # Si no había datos en las filas seleccionadas, informa al usuario.
            mostrar_mensaje("⚠ Las filas seleccionadas no tienen datos", "yellow")

    # 📋 Evento: doble clic medio en una fila copia los datos de esa fila.
    def copiar_si_doble_click(event):
        # Identifica la fila bajo la coordenada Y del evento.
        item_id = tabla.identify_row(event.y)
        if item_id:
            # Selecciona la fila y llama a copiar_fila para llevarla al portapapeles.
            tabla.selection_set(item_id)
            copiar_fila()

    # Dependiendo del sistema, "<Double-2>" puede corresponder al doble clic con la rueda del mouse.
    tabla.bind("<Double-2>", copiar_si_doble_click)   # doble clic rueda del mouse
    # Permite también copiar mediante Ctrl + C cuando haya filas seleccionadas.
    tabla.bind("<Control-c>", copiar_fila)           # Ctrl + C



    # ---------------------- MENSAJES ----------------------
    # Label destinado a mostrar mensajes temporales (errores, confirmaciones, info).
    mensaje_label = ctk.CTkLabel(
        parent,  # Contenedor principal.
        text="", # Empieza vacío.
        font=("Arial", 14, "bold")  # Fuente Arial, tamaño 14, en negrita.
    )
     # Muestra la etiqueta con un margen superior de 5 píxeles y sin margen inferior.
    mensaje_label.pack(pady=(0, 8))



    # ---------------------- FUNCIÓN PARA MOSTRAR MENSAJES ----------------------
    def mostrar_mensaje(texto, color):
        """
        Muestra un mensaje en mensaje_label con el color indicado y lo borra pasado un tiempo.
        - texto: cadena a mostrar
        - color: color del texto (ej. "green", "yellow", "red", "cyan")
        """

        mensaje_label.configure(text=texto, text_color=color)
        # Borra el mensaje después de 3,5 segundos para no saturar la interfaz.
        parent.after(3500, lambda: mensaje_label.configure(text=""))

    
    
    # ---------------------- BOTÓN PARA ACCEDER AL PANEL DE PAGOS ----------------------
    boton_volver = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Administrar pagos",  # Texto que muestra el botón.
        command=lambda: mostrar_administrar_pagos(parent, lambda: mostrar_patreon_drago(parent, volver_callback, boton_font), boton_font),  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles.
        height=50,  # Alto en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_volver.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.
    


    # ---------------------- BOTÓN PARA VOLVER AL MENÚ PRINCIPAL ----------------------
    boton_volver = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Volver al menú principal",  # Texto que muestra el botón.
        command=volver_callback,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles.
        height=50,  # Alto en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_volver.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.