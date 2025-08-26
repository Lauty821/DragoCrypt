# Importa la biblioteca "customtkinter" y la renombra como "ctk"
# CustomTkinter es una versión mejorada de Tkinter con soporte para temas, colores y widgets modernos.
import customtkinter as ctk  

# Importa desde tkinter el módulo "filedialog" para mostrar cuadros de diálogo
# que permiten seleccionar archivos o carpetas en el sistema operativo.
from tkinter import filedialog  

# Importa la biblioteca estándar "os" para trabajar con rutas, nombres de archivos, carpetas y funciones del sistema operativo.
import os  


# ---------------------- FUNCIÓN PARA MARCAR UN ARCHIVO ----------------------
def marcar(archivo, texto_marca):
    """
    Abre un archivo en modo binario y añade al final un texto como "marca".
    - archivo: ruta completa al archivo que se quiere modificar.
    - texto_marca: texto que se agregará al final del archivo.
    """

    # Abre el archivo indicado en modo "ab" (append binario).
    # Esto significa que no borra lo que ya existe, solo añade al final en formato binario.
    with open(archivo, "ab") as f:  
        # Convierte el texto a bytes usando codificación UTF-8 para poder escribirlo en modo binario.
        f.write(texto_marca.encode("utf-8"))  



# ---------------------- FUNCIÓN PARA MOSTRAR LA PANTALLA DE MARCAR ARCHIVOS ----------------------
def mostrar_marcar_archivos(parent, volver_callback, boton_font):
    """
    Crea y muestra la interfaz gráfica para seleccionar y marcar archivos.
    - parent: contenedor principal donde se colocarán los elementos gráficos.
    - volver_callback: función que se ejecutará cuando se presione el botón "Volver".
    - boton_font: tipo de fuente (familia, tamaño, estilo) que se usará en los botones.
    """

    # Se vuelven a importar os y filedialog aquí por si se quiere usar esta función de forma independiente.
    import os
    from tkinter import filedialog

    # Recorre todos los widgets que ya existen dentro de "parent" y los oculta/borra de la pantalla.
    for widget in parent.winfo_children():
        widget.pack_forget()



    # ---------------------- TÍTULO ----------------------
    # Crea una etiqueta (Label) con el título de la pantalla.
    titulo = ctk.CTkLabel(
        parent,  # Contenedor donde se coloca el texto.
        text="Marcar Archivos",  # Texto que se muestra.
        font=("Arial", 22, "bold")  # Fuente: tamaño 22, negrita ("bold").
    )
    # Empaqueta (muestra) el título con un margen vertical de 20 píxeles arriba y abajo.
    titulo.pack(pady=12)


    # ---------------------- LISTA DE ARCHIVOS SELECCIONADOS ----------------------
    # Lista en memoria donde se guardan las rutas completas de los archivos que el usuario elija.
    lista_archivos = []

    # Crea un marco (frame) con fondo blanco para contener la lista de archivos.
    panel_frame = ctk.CTkFrame(
        parent,  # Contenedor principal.
        fg_color="white"  # Color de fondo del marco.
    )
    panel_frame.pack(pady=10)  # Muestra el marco con un margen vertical de 10 píxeles.

    # Crea un cuadro de texto para mostrar los nombres de los archivos seleccionados.
    panel_widget = ctk.CTkTextbox(
        panel_frame,  # Lo coloca dentro del marco "panel_frame".
        width=500,  # Ancho de 500 píxeles.
        height=200,  # Alto de 200 píxeles.
        fg_color="white",    # Color de fondo (blanco).
        text_color="black"  # Color del texto (negro).
    )
    # Inhabilita la edición del panel para que sea solo lectura inicialmente.
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
        # Usa "after" para ejecutar una función después de 3300 ms (3,3 segundos).
        # Aquí se usa para vaciar el texto después del tiempo.
        parent.after(3300, lambda: mensaje_label.configure(text=""))  



    # ---------------------- FUNCIÓN PARA ACTUALIZAR LISTA ----------------------
    def actualizar_lista():
        """
        Refresca el contenido del cuadro de texto con los nombres de los archivos seleccionados.
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

        # Si la lista tiene archivos, activa el botón de eliminar; si está vacía, lo desactiva.
        if lista_archivos:
            boton_eliminar.configure(state="normal")
        else:
            boton_eliminar.configure(state="disabled")  



    # ---------------------- FUNCIÓN PARA AGREGAR ARCHIVOS ----------------------
    def seleccionar_archivos():
        """
        Abre un cuadro de diálogo para seleccionar uno o más archivos y agregarlos a la lista.
        """

        # Muestra el diálogo de selección de archivos, permitiendo cualquier tipo (*.*).
        seleccionados = filedialog.askopenfilenames(
            title="Seleccionar archivos", 
            filetypes=[("Todos los archivos", "*.*")]
        )

        # Recorre los archivos seleccionados.
        for archivo in seleccionados:
            # Solo los agrega si no están ya en la lista (evita duplicados).
            if archivo not in lista_archivos:  
                lista_archivos.append(archivo)
        # Actualiza la lista mostrada en pantalla.
        actualizar_lista()  



    # ---------------------- FUNCIÓN PARA ELIMINAR ARCHIVOS ----------------------
    def eliminar_archivos():
        """
        Elimina de la lista los archivos que el usuario seleccionó en el cuadro de texto.
        """

        # Si no hay nada seleccionado en el cuadro de texto, muestra advertencia y sale.
        if not panel_widget.tag_ranges("sel"):
            mostrar_mensaje("⚠ Debes seleccionar al menos un archivo", "yellow")
            return

        # Obtiene el texto seleccionado y lo separa en líneas (pueden ser varios nombres).
        seleccion = panel_widget.get("sel.first", "sel.last").strip().split("\n")

        # Busca en la lista completa las rutas que coincidan con esos nombres.
        rutas_a_eliminar = [ruta for ruta in lista_archivos if os.path.basename(ruta) in seleccion]

        # Recorre y elimina esas rutas de la lista principal.
        for ruta in rutas_a_eliminar:
            lista_archivos.remove(ruta)  
        # Refresca la lista en pantalla.
        actualizar_lista()  



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



    # ---------------------- BOTÓN PARA ELIMINAR ARCHIVOS ----------------------
    boton_eliminar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Eliminar archivos seleccionados",  # Texto que muestra el botón.
        state="disabled",  # Comienza deshabilitado hasta que haya archivos en la lista.
        width=280,  # Ancho del botón en píxeles.
        height=50,  # Alto del botón en píxeles.
        font=boton_font,  # Fuente usada para el texto.
        command=eliminar_archivos  # Función que se ejecuta al hacer clic.
    )
    boton_eliminar.pack(pady=6)  # Muestra el botón con margen vertical de 6 píxeles.



    # ---------------------- ETIQUETA PARA TEXTO DE LA MARCA ----------------------
    etiqueta_marca = ctk.CTkLabel(
        parent,  # Contenedor principal.
        text="Texto de la marca:",  # Texto que muestra el botón.
        font=boton_font  # Fuente usada para el texto.
    )
    etiqueta_marca.pack(pady=(10, 0))  # Muestra con margen superior de 10 píxeles y sin margen inferior.



    # ---------------------- CAMPO DE TEXTO PARA ENTRADA DE MARCA ----------------------
    entrada_marca = ctk.CTkTextbox(
        parent,  # Contenedor principal.
        width=350,  # Ancho en píxeles.
        height=120,  # Alto en píxeles.
        fg_color="white",  # Color de fondo blanco.
        text_color="black",  # Color del texto negro.
        corner_radius=8  # Bordes redondeados con radio de 8 píxeles.
    )
    entrada_marca.pack(pady=(0, 10))  # Muestra el campo con margen inferior de 10 píxeles.



    # ---------------------- FUNCIÓN PARA MARCAR ARCHIVOS ----------------------
    def marcar_archivos_botones():
        """
        Aplica la marca escrita en "entrada_marca" a todos los archivos seleccionados.
        """
        
        # Obtiene el texto escrito por el usuario (desde la posición inicial hasta el final) y le quita espacios extra.
        texto_marca = entrada_marca.get("1.0", "end").strip()  

        # Si no hay archivos en la lista, muestra advertencia y termina.
        if not lista_archivos:  
            mostrar_mensaje("⚠ No has seleccionado ningún archivo", "yellow")
            return
        # Si no hay texto para la marca, muestra advertencia y termina.
        if not texto_marca:  
            mostrar_mensaje("⚠ Ingresa un texto para agregar como marca", "yellow")
            return

        # Recorre todos los archivos seleccionados y les aplica la marca.
        for archivo in lista_archivos:
            try:
                marcar(archivo, texto_marca)
            except Exception as e:
                # Si ocurre un error, muestra mensaje y termina el proceso.
                mostrar_mensaje(f"Error con {archivo}: {e}", "red")
                return

        # Si todos se marcaron correctamente, muestra confirmación.
        mostrar_mensaje("✔ Archivos marcados correctamente", "green")  



    # ---------------------- BOTÓN PARA MARCAR ARCHIVOS ----------------------
    boton_marcar = ctk.CTkButton(
        parent,  # Contenedor principal.
        text="Marcar archivos",  # Texto que muestra el botón.
        command=marcar_archivos_botones,  # Función que se ejecuta al hacer clic.
        width=280,  # Ancho en píxeles.
        height=50,  # Alto en píxeles.
        font=boton_font  # Fuente usada para el texto.
    )
    boton_marcar.pack(pady=6)  # Muestra el campo con margen inferior de 10 píxeles.



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