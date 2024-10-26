import sqlite3

# Conexión a la base de datos SQLite
conn = sqlite3.connect('registro_clases.db', check_same_thread=False)
cursor = conn.cursor()

# Función para crear las tablas
def crear_tablas():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Profesor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Materia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            profesor_id INTEGER,
            FOREIGN KEY(profesor_id) REFERENCES Profesor(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER,
            dia TEXT NOT NULL,
            hora TEXT NOT NULL,
            fecha DATE,
            impartida BOOLEAN,
            FOREIGN KEY(materia_id) REFERENCES Materia(id)
        )
    ''')

    conn.commit()
