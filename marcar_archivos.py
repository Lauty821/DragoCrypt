import customtkinter as ctk  # Esto importa la versión moderna de Tkinter con soporte para temas.
from tkinter import filedialog  # Esto permite abrir cuadros de diálogo para seleccionar archivos o carpetas.
import os  # Esto permite interactuar con el sistema de archivos (rutas, nombres de archivos, etc.)


# Esta esta es la función marca un archivo.
def marcar(archivo, texto_marca):
    """
    Esto abre un archivo en modo binario append y agrega el texto de la marca.
    - archivo: ruta completa del archivo a marcar.
    - texto_marca: string que se añadirá al final del archivo.
    """
    
    with open(archivo, "ab") as f:  # Esto lo abre en modo append binario.
        f.write(texto_marca.encode("utf-8"))  # Acá escribimos la marca codificada en bytes.



# Esta es la función para mostrar la pantalla de marcar archivos.
def mostrar_marcar_archivos(parent, volver_callback, boton_font):
    """
    Esto construye toda la interfaz de marcar archivos dentro del contenedor 'parent'.
    - parent: contenedor Tkinter donde se mostrará la interfaz.
    - volver_callback: función a ejecutar al presionar el botón "Volver".
    - boton_font: fuente para los botones.
    """

    import os
    from tkinter import filedialog

    # Esto sirve para limpiar pantalla borrando cualquier widget previo.
    for widget in parent.winfo_children():
        widget.pack_forget()


    # Este es el título de la pantalla.
    titulo = ctk.CTkLabel(parent, text="Pantalla de Marcar Archivos", font=("Arial", 20, "bold"))
    titulo.pack(pady=20)


    # Esta es la lista que guarda las rutas completas de los archivos seleccionados.
    lista_archivos = []


    # Este es el contenedor para la lista de archivos.
    lista_frame = ctk.CTkFrame(parent, fg_color="white")
    lista_frame.pack(pady=10)


    # Este es el widget de texto donde se muestran los nombres de archivos.
    lista_widget = ctk.CTkTextbox(lista_frame, width=500, height=200, fg_color="white", text_color="black")
    lista_widget.configure(state="disabled")  # Solo lectura inicialmente
    lista_widget.pack()


    # Etiqueta para mostrar mensajes temporales (errores, confirmaciones)
    mensaje_label = ctk.CTkLabel(parent, text="", font=("Arial", 14, "bold"))
    mensaje_label.pack(pady=(5, 0))



    # Esta función sirve para mostrar mensajes temporales.
    def mostrar_mensaje(texto, color):
        mensaje_label.configure(text=texto, text_color=color)  # Cambia el texto y color
        parent.after(2500, lambda: mensaje_label.configure(text=""))  # Borra el mensaje tras 2.5s



    # Esta función sirve para actualizar la lista de archivos en el widget.
    def actualizar_lista():
        lista_widget.configure(state="normal")  # Esto sirve para habilitar edición temporal.
        lista_widget.delete("1.0", "end")  # Esto sirve para limpiar contenido previo.
        for archivo in lista_archivos:
            lista_widget.insert("end", os.path.basename(archivo) + "\n")  # Esto sirve para insertar solo el nombre del archivo.
        lista_widget.configure(state="disabled")  # Esto sirve para deshabilitar edición nuevamente.

        # Esto sirve para activar o desactivar el botón de eliminar según haya archivos.
        if lista_archivos:
            boton_eliminar.configure(state="normal")
        else:
            boton_eliminar.configure(state="disabled")



    # Esta función sirve para agregar archivos a la lista.
    def agregar_archivos():
        seleccionados = filedialog.askopenfilenames(
            title="Seleccionar archivos", 
            filetypes=[("Todos los archivos", "*.*")]  # Estto permite seleccionar cualquier tipo de archivo.
        )
        for archivo in seleccionados:
            if archivo not in lista_archivos:  # Esto evita archivos duplicados.
                lista_archivos.append(archivo)
        actualizar_lista()  # Esto sirve para refrescar la lista visible.



    # Esta función sirve para eliminar archivos seleccionados.
    def eliminar_archivos():
        # Esto verifica si hay selección en el widget, sino muestra advertencia.
        if not lista_widget.tag_ranges("sel"):
            mostrar_mensaje("⚠ Debes seleccionar al menos un archivo", "yellow")
            return

        # Esto obtiene los nombres de archivos seleccionados.
        seleccion = lista_widget.get("sel.first", "sel.last").strip().split("\n")
        # Esto mapea los nombres seleccionados a sus rutas completas.
        rutas_a_eliminar = [ruta for ruta in lista_archivos if os.path.basename(ruta) in seleccion]
        for ruta in rutas_a_eliminar:
            lista_archivos.remove(ruta)  # Esto elimina de la lista interna.
        actualizar_lista()  # Esto actualiza la lista en pantalla.



    # Estos ya serian los botones de la interfaz.
    # Este es el botón para seleccionar archivos.
    boton_seleccionar = ctk.CTkButton(
        parent, 
        text="Seleccionar archivos", 
        command=agregar_archivos,
        width=280, height=50, font=boton_font
    )
    boton_seleccionar.pack(pady=6)


    # Este es el botón para eliminar archivos seleccionados.
    boton_eliminar = ctk.CTkButton(
        parent, 
        text="Eliminar archivos seleccionados", 
        state="disabled",  # Inicialmente el boton esta deshabilitado.
        width=280, height=40, font=boton_font, 
        command=eliminar_archivos
    )
    boton_eliminar.pack(pady=6)

    # Esta es la etiqueta que indica dónde escribir la marca.
    etiqueta_marca = ctk.CTkLabel(parent, text="Texto de la marca:", font=boton_font)
    etiqueta_marca.pack(pady=(10, 0))

    # Cuadro de texto donde el usuario ingresa la marca
    entrada_marca = ctk.CTkTextbox(
        parent, width=350, height=120, fg_color="white", text_color="black", corner_radius=8
    )
    entrada_marca.pack(pady=(0, 10))


    
    # Esta función es la que aplica la marca a los archivos seleccionados.
    def marcar_archivos_botones():
        texto_marca = entrada_marca.get("1.0", "end").strip()  # Esto obtiene el contenido del textbox.
        if not lista_archivos:  # Si no hay archivos, muestra un mensaje.
            mostrar_mensaje("⚠ No has seleccionado ningún archivo", "yellow")
            return
        if not texto_marca:  # Si no hay texto, muestra un mensaje.
            mostrar_mensaje("⚠ Ingresa un texto para agregar como marca", "yellow")
            return
        # Esto recorre cada archivo y aplica la marca.
        for archivo in lista_archivos:
            try:
                marcar(archivo, texto_marca)
            except Exception as e:
                mostrar_mensaje(f"Error con {archivo}: {e}", "red")
                return
        mostrar_mensaje("✔ Archivos marcados correctamente", "green")


    # Este es el botón que ejecuta el marcado.
    boton_marcar = ctk.CTkButton(
        parent, text="Marcar archivos", command=marcar_archivos_botones,
        width=280, height=50, font=boton_font
    )
    boton_marcar.pack(pady=12)


    # Este es el botón para volver al menú principal.
    boton_volver = ctk.CTkButton(
        parent, text="Volver al menú principal",
        command=volver_callback, width=280, height=50, font=boton_font
    )
    boton_volver.pack(pady=12)