import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import atexit

# Conectar a la base de datos SQLite
conn = sqlite3.connect("urbanizacion.db")
cursor = conn.cursor()

# Crear tablas de vecinos y pagos si no existen
cursor.execute(
    """CREATE TABLE IF NOT EXISTS vecinos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_lote TEXT,
                    nombre TEXT,
                    apellido TEXT,
                    telefono TEXT,
                    estado TEXT)"""
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vecino_id INTEGER,
                    mes TEXT,
                    cuota REAL,
                    pagado REAL,
                    detalles TEXT,
                    FOREIGN KEY(vecino_id) REFERENCES vecinos(id))"""
)
conn.commit()


# Cerrar la conexión a la base de datos al salir
def cerrar_conexion():
    conn.close()


atexit.register(cerrar_conexion)


# Funciones
def actualizar_estado_vecino(id_vecino):
    cursor.execute(
        "SELECT SUM(cuota) - SUM(pagado) FROM pagos WHERE vecino_id=?", (id_vecino,)
    )
    saldo_total = cursor.fetchone()[0] or 0

    if saldo_total == 0:
        estado = "Al día"
    elif saldo_total < 0:
        estado = "Saldo a favor"
    else:
        estado = "Tiene deuda"

    cursor.execute("UPDATE vecinos SET estado=? WHERE id=?", (estado, id_vecino))
    conn.commit()


def limpiar_entradas():
    numero_lote_var.set("")
    nombre_var.set("")
    apellido_var.set("")
    telefono_var.set("")


def agregar_vecino():
    numero_lote = numero_lote_var.get()
    nombre = nombre_var.get()
    apellido = apellido_var.get()
    telefono = telefono_var.get()

    if numero_lote and nombre and apellido and telefono:
        cursor.execute(
            "INSERT INTO vecinos (numero_lote, nombre, apellido, telefono, estado) VALUES (?, ?, ?, ?, 'Al día')",
            (numero_lote, nombre, apellido, telefono),
        )
        conn.commit()
        actualizar_tabla_vecinos()
        limpiar_entradas()
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")


def editar_vecino():
    nombre = nombre_var.get()
    apellido = apellido_var.get()
    vecino = obtener_vecino_por_nombre_apellido(nombre, apellido)
    if vecino:
        numero_lote = numero_lote_var.get()
        nuevo_nombre = nombre_var.get()
        nuevo_apellido = apellido_var.get()
        telefono = telefono_var.get()
        estado = vecino[5]
        cursor.execute(
            "UPDATE vecinos SET numero_lote=?, nombre=?, apellido=?, telefono=?, estado=? WHERE id=?",
            (numero_lote, nuevo_nombre, nuevo_apellido, telefono, estado, vecino[0]),
        )
        conn.commit()
        actualizar_tabla_vecinos()
        limpiar_entradas()
    else:
        messagebox.showwarning("Advertencia", "Vecino no encontrado")


def eliminar_vecino():
    nombre = nombre_var.get()
    apellido = apellido_var.get()
    vecino = obtener_vecino_por_nombre_apellido(nombre, apellido)
    if vecino:
        cursor.execute("DELETE FROM vecinos WHERE id=?", (vecino[0],))
        cursor.execute("DELETE FROM pagos WHERE vecino_id=?", (vecino[0],))
        conn.commit()
        actualizar_tabla_vecinos()
        limpiar_entradas()
    else:
        messagebox.showwarning("Advertencia", "Vecino no encontrado")


def obtener_vecino_por_nombre_apellido(nombre, apellido):
    cursor.execute(
        "SELECT * FROM vecinos WHERE nombre=? AND apellido=?", (nombre, apellido)
    )
    return cursor.fetchone()


def actualizar_tabla_vecinos():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM vecinos")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)


def mostrar_informacion_vecino():
    selected_item = tree.focus()
    if selected_item:
        valores = tree.item(selected_item, "values")
        id_vecino = valores[0]
        ventana_informacion(id_vecino)
    else:
        messagebox.showwarning(
            "Advertencia", "Selecciona un vecino para mostrar información"
        )


def ventana_informacion(id_vecino):
    ventana = tk.Toplevel()
    ventana.title("Información del Vecino")

    cursor.execute("SELECT * FROM pagos WHERE vecino_id=?", (id_vecino,))
    pagos = cursor.fetchall()

    columns = ("Mes", "Cuota", "Pagado", "Detalles", "Saldo")
    tree_info = ttk.Treeview(ventana, columns=columns, show="headings")
    for col in columns:
        tree_info.heading(col, text=col)
    tree_info.grid(row=0, column=0, columnspan=4)

    global saldo_total
    saldo_total = 0
    for pago in pagos:
        mes, cuota, pagado, detalles = pago[2], pago[3], pago[4], pago[5]
        saldo = pagado - cuota
        saldo_total += saldo
        tree_info.insert("", "end", values=(mes, cuota, pagado, detalles, saldo))

    # Mostrar el saldo total
    tk.Label(ventana, text=f"Saldo Total: {saldo_total}").grid(
        row=1, column=0, columnspan=4
    )

    tk.Button(
        ventana, text="Añadir Pago", command=lambda: anadir_pago(id_vecino, ventana)
    ).grid(row=2, column=0)
    tk.Button(
        ventana,
        text="Editar Pago",
        command=lambda: editar_pago(id_vecino, tree_info, ventana),
    ).grid(row=2, column=1)


def anadir_pago(id_vecino, parent_window):
    ventana_pago = tk.Toplevel(parent_window)
    ventana_pago.title("Añadir Pago")

    tk.Label(ventana_pago, text="Mes").grid(row=0, column=0)
    entry_mes = tk.Entry(ventana_pago)
    entry_mes.grid(row=0, column=1)

    tk.Label(ventana_pago, text="Cuota").grid(row=1, column=0)
    entry_cuota = tk.Entry(ventana_pago)
    entry_cuota.grid(row=1, column=1)

    tk.Label(ventana_pago, text="Pagado").grid(row=2, column=0)
    entry_pagado = tk.Entry(ventana_pago)
    entry_pagado.grid(row=2, column=1)

    tk.Label(ventana_pago, text="Detalles").grid(row=3, column=0)
    entry_detalles = tk.Entry(ventana_pago)
    entry_detalles.grid(row=3, column=1)

    def guardar_pago():
        mes = entry_mes.get()
        cuota = float(entry_cuota.get())
        pagado = float(entry_pagado.get())
        detalles = entry_detalles.get()

        if mes and cuota and pagado and detalles:
            cursor.execute(
                "INSERT INTO pagos (vecino_id, mes, cuota, pagado, detalles) VALUES (?, ?, ?, ?, ?)",
                (id_vecino, mes, cuota, pagado, detalles),
            )
            conn.commit()
            actualizar_estado_vecino(id_vecino)
            ventana_pago.destroy()
            parent_window.destroy()  # Cerrar la ventana de información actual
            actualizar_tabla_vecinos()  # Actualizar la tabla de vecinos en la ventana principal
            mostrar_informacion_vecino()  # Volver a abrir la ventana de información actualizada
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")

    tk.Button(ventana_pago, text="Guardar", command=guardar_pago).grid(
        row=4, column=0, columnspan=2
    )


def editar_pago(id_vecino, tree_info, parent_window):
    selected_item = tree_info.focus()
    if selected_item:
        valores = tree_info.item(selected_item, "values")
        mes = valores[0]

        cursor.execute(
            "SELECT * FROM pagos WHERE vecino_id=? AND mes=?", (id_vecino, mes)
        )
        pago = cursor.fetchone()

        if pago:
            ventana_pago = tk.Toplevel()
            ventana_pago.title("Editar Pago")

            tk.Label(ventana_pago, text="Mes").grid(row=0, column=0)
            entry_mes = tk.Entry(ventana_pago)
            entry_mes.grid(row=0, column=1)
            entry_mes.insert(0, pago[2])

            tk.Label(ventana_pago, text="Cuota").grid(row=1, column=0)
            entry_cuota = tk.Entry(ventana_pago)
            entry_cuota.grid(row=1, column=1)
            entry_cuota.insert(0, pago[3])

            tk.Label(ventana_pago, text="Pagado").grid(row=2, column=0)
            entry_pagado = tk.Entry(ventana_pago)
            entry_pagado.grid(row=2, column=1)
            entry_pagado.insert(0, pago[4])

            tk.Label(ventana_pago, text="Detalles").grid(row=3, column=0)
            entry_detalles = tk.Entry(ventana_pago)
            entry_detalles.grid(row=3, column=1)
            entry_detalles.insert(0, pago[5])

            def guardar_pago():
                cuota = float(entry_cuota.get())
                pagado = float(entry_pagado.get())
                detalles = entry_detalles.get()

                if cuota and pagado and detalles:
                    cursor.execute(
                        "UPDATE pagos SET cuota=?, pagado=?, detalles=? WHERE vecino_id=? AND mes=?",
                        (cuota, pagado, detalles, id_vecino, mes),
                    )
                    conn.commit()
                    actualizar_estado_vecino(id_vecino)
                    ventana_pago.destroy()
                    parent_window.destroy()  # Cerrar la ventana de información actual
                    actualizar_tabla_vecinos()  # Actualizar la tabla de vecinos en la ventana principal
                    mostrar_informacion_vecino()  # Volver a abrir la ventana de información actualizada
                else:
                    messagebox.showwarning(
                        "Advertencia", "Todos los campos son obligatorios"
                    )

            tk.Button(ventana_pago, text="Guardar", command=guardar_pago).grid(
                row=4, column=0, columnspan=2
            )
        else:
            messagebox.showwarning("Advertencia", "Pago no encontrado")
    else:
        messagebox.showwarning("Advertencia", "Selecciona un pago para editar")


# Configuración de la interfaz gráfica principal
root = tk.Tk()
root.title("Administración de Urbanización")

numero_lote_var = tk.StringVar()
nombre_var = tk.StringVar()
apellido_var = tk.StringVar()
telefono_var = tk.StringVar()

tk.Label(root, text="Número de Lote").grid(row=0, column=0)
tk.Entry(root, textvariable=numero_lote_var).grid(row=0, column=1)

tk.Label(root, text="Nombre").grid(row=1, column=0)
tk.Entry(root, textvariable=nombre_var).grid(row=1, column=1)

tk.Label(root, text="Apellido").grid(row=2, column=0)
tk.Entry(root, textvariable=apellido_var).grid(row=2, column=1)

tk.Label(root, text="Teléfono").grid(row=3, column=0)
tk.Entry(root, textvariable=telefono_var).grid(row=3, column=1)

tk.Button(root, text="Agregar Vecino", command=agregar_vecino).grid(row=4, column=0)
tk.Button(root, text="Editar Vecino", command=editar_vecino).grid(row=4, column=1)
tk.Button(root, text="Eliminar Vecino", command=eliminar_vecino).grid(row=4, column=2)

columns = ("ID", "Número de Lote", "Nombre", "Apellido", "Teléfono", "Estado")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=4)

tk.Button(root, text="Mostrar Información", command=mostrar_informacion_vecino).grid(
    row=6, column=0, columnspan=4
)

actualizar_tabla_vecinos()

root.mainloop()
