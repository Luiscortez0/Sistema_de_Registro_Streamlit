from database import conn, cursor
import pandas as pd

# Obtener todos los profesores (sin argumentos)
def obtener_profesores():
    """
    Obtiene todos los profesores de la tabla "Profesor"
    """
    cursor.execute("SELECT id, nombre FROM Profesor")
    return cursor.fetchall()

# Obtener todas las materias (sin argumentos)
def obtener_materias():
    """
    Obtiene todas las materias de la tabla "Materia"
    """
    cursor.execute("SELECT id, nombre FROM Materia")
    return cursor.fetchall()

# Registrar asistencia con día, hora y fecha (argumentos posicionales y nombrados)
def registrar_asistencia(materia_id, hora, fecha="CURRENT_DATE", impartida=True):
    """
    Registra la asistencia a una clase.
    
    Args:
        materia_id (int): ID de la materia.
        hora (str): Hora de la clase.
        fecha (str, opcional): Fecha de la clase. Por defecto, la fecha actual.
        impartida (bool, opcional): Si la clase fue impartida o no. Por defecto, True.
    """
    cursor.execute('''
        INSERT INTO Asistencia (materia_id, hora, fecha, impartida) 
        VALUES (?, ?, ?, ?)
    ''', (materia_id, hora, fecha, impartida))
    conn.commit()

# Exportar asistencias a CSV (sin argumentos)
def exportar_asistencias_a_csv():
    """
    Exporta todas las asistencias registradas a un archivo CSV.
    """
    query = '''
        SELECT p.nombre AS profesor, m.nombre AS materia, a.hora, a.fecha, a.impartida
        FROM Asistencia a
        JOIN Materia m ON a.materia_id = m.id
        JOIN Profesor p ON m.profesor_id = p.id
    '''
    df = pd.read_sql_query(query, conn)
    df.to_csv("asistencias.csv", index=False)

# Generar estadísticas de asistencia (argumentos con valores por defecto)
def generar_estadisticas_asistencia_filtrada(tipo_reporte="Global", profesor_id=None, materia_id=None):
    """
    Genera estadísticas de asistencia filtradas por profesor o materia, incluyendo si la clase fue impartida o no.
    
    Args:
        tipo_reporte (str, opcional): Tipo de reporte, puede ser "Por Profesor", "Por Materia", o "Global". 
        profesor_id (int, opcional): ID del profesor para filtrar las estadísticas. 
        materia_id (int, opcional): ID de la materia para filtrar las estadísticas.
    
    Returns:
        list: Resultados del reporte detallados con información de si la clase fue impartida.
        dict: Un resumen con el total de clases, clases impartidas y clases no impartidas.
    """
    if tipo_reporte == "Por Profesor" and profesor_id:
        query = '''
            SELECT a.fecha, a.impartida
            FROM Asistencia a
            JOIN Materia m ON a.materia_id = m.id
            JOIN Profesor p ON m.profesor_id = p.id
            WHERE p.id = ?
            ORDER BY a.fecha
        '''
        cursor.execute(query, (profesor_id,))
    elif tipo_reporte == "Por Materia" and materia_id:
        query = '''
            SELECT a.fecha, a.impartida
            FROM Asistencia a
            JOIN Materia m ON a.materia_id = m.id
            WHERE m.id = ?
            ORDER BY a.fecha
        '''
        cursor.execute(query, (materia_id,))
    else:  # Global
        query = '''
            SELECT a.fecha, a.impartida
            FROM Asistencia a
            ORDER BY a.fecha
        '''
        cursor.execute(query)
    
    # Obtener resultados detallados por fecha
    resultados = cursor.fetchall()

    # Resumen para mostrar por separado
    resumen = {
        'total_clases': len(resultados),
        'clases_impartidas': sum(1 for r in resultados if r[1] == 1),
        'clases_no_impartidas': sum(1 for r in resultados if r[1] == 0)
    }
    
    return resultados, resumen

# Crear nuevo profesor y asignar materia
def crear_profesor_materia(nombre_profesor, nombre_materia):
    """
    Inserta un nuevo registro de un profesor a la tabla "Profesor"
    y una nueva materia a la tabla "Materia" y los enlaza
    """
    # Insertar nuevo profesor
    cursor.execute('''
        INSERT INTO Profesor (nombre) VALUES (?)
    ''', (nombre_profesor,))
    conn.commit()
    
    # Obtener el ID del profesor recién creado
    cursor.execute('SELECT id FROM Profesor WHERE nombre = ?', (nombre_profesor,))
    profesor_id = cursor.fetchone()[0]
    
    # Insertar nueva materia con el id del profesor
    cursor.execute('''
        INSERT INTO Materia (nombre, profesor_id) VALUES (?, ?)
    ''', (nombre_materia, profesor_id))
    conn.commit()

    return profesor_id  # Retornamos el ID del profesor recién creado

# Eliminar un profesor y sus materias asociadas
def eliminar_profesor_y_materias(profesor_id):
    """
    Elimina un registro de algun profesor de la tabla "Profesor"
    y todas las materias asociadas de la tabla "Materia"
    """
    # Eliminar materias asociadas al profesor
    cursor.execute('''
        DELETE FROM Materia WHERE profesor_id = ?
    ''', (profesor_id,))
    conn.commit()

    # Eliminar profesor
    cursor.execute('''
        DELETE FROM Profesor WHERE id = ?
    ''', (profesor_id,))
    conn.commit()

