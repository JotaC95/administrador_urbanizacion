import sqlite3

# Crear base de datos y tablas
conn = sqlite3.connect('urbanizacion.db')
c = conn.cursor()

# Tabla vecinos
c.execute('''
    CREATE TABLE IF NOT EXISTS vecinos (
        id INTEGER PRIMARY KEY,
        numero_lote TEXT,
        nombre TEXT,
        apellido TEXT,
        telefono TEXT,
        estado TEXT
    )
''')

# Tabla pagos
c.execute('''
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY,
        vecino_id INTEGER,
        mes TEXT,
        cuota REAL,
        pagado REAL,
        detalles TEXT,
        saldo REAL,
        FOREIGN KEY(vecino_id) REFERENCES vecinos(id)
    )
''')

conn.commit()
conn.close()
