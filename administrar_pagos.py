import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ---------------------------
# Ventana de administrar pagos
# ---------------------------
def mostrar_administrar_pagos(parent, usuarios):
    """
    Abre una ventana secundaria con la tabla de administración de pagos.
    - parent: ventana principal
    - usuarios: lista de usuarios cargados en la tabla principal (columna Usuario Telegram)
    """

    # Crear ventana toplevel
    ventana = ctk.CTkToplevel(parent)
    ventana.title("Administrar Pagos")
    ventana.geometry("800x400")

    # Frame contenedor
    frame = ctk.CTkFrame(ventana, fg_color="#212121", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=12, pady=8)

    # Scrollbars
    scrollbar_y = ctk.CTkScrollbar(frame, orientation="vertical")
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x = ctk.CTkScrollbar(frame, orientation="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    # Tabla Treeview
    columnas = ("usuario", "pago", "meses_abonados", "vencimiento")
    tabla = ttk.Treeview(
        frame,
        columns=columnas,
        show="headings",
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tabla.heading("usuario", text="Usuario Telegram")
    tabla.heading("pago", text="Pagó")
    tabla.heading("meses_abonados", text="Meses abonados")
    tabla.heading("vencimiento", text="Vencimiento")

    tabla.column("usuario", width=150)
    tabla.column("pago", width=80)
    tabla.column("meses_abonados", width=200)
    tabla.column("vencimiento", width=120)

    tabla.pack(fill="both", expand=True)

    # Vincular scrollbars
    scrollbar_y.configure(command=tabla.yview)
    scrollbar_x.configure(command=tabla.xview)

    # Insertar usuarios automáticamente
    for usuario in usuarios:
        tabla.insert("", "end", values=(usuario, "No", "", ""))

    # Ejemplo de cómo actualizar vencimiento (cuando el usuario abone)
    def actualizar_vencimiento(item_id, meses):
        try:
            # último mes en formato YYYY-MM
            ultimo = datetime.strptime(meses[-1], "%Y-%m")
            vencimiento = (ultimo + relativedelta(months=1)).strftime("%Y-%m-%d")
        except Exception:
            vencimiento = ""
        valores = list(tabla.item(item_id, "values"))
        valores[3] = vencimiento
        tabla.item(item_id, values=valores)

    return ventana
