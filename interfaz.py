import streamlit as st
from funciones import *
from database import crear_tablas
import pandas as pd
from datetime import datetime

# Ejecutar la creación de tablas al inicio
crear_tablas()

# Función principal de la aplicación
def main():
    st.title("Sistema de Registro de Asistencia Docente")

    menu = ["Ver Horario", "Registrar Asistencia", "Generar Estadísticas", "Gestionar Profesores y Materias", "Exportar Asistencias"]
    choice = st.sidebar.selectbox("Menú", menu)

    # Mostrar Horario de Clases
    if choice == "Ver Horario":
        st.subheader("Horario de Clases")
        data = {
            "Hora": ["7:00 - 8:00", "8:00 - 8:40", "8:45 - 9:15", "9:15 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00"],
            "Lunes": ["ED", "ED", "RECESO", "PF", "PF", "(IR)", "I III", "I III", "MN"],
            "Martes": [" ", "(ED)", "RECESO", "ED", "ED", "I III", "(I III)", "PF", " "],
            "Miércoles": ["(SDE)", "ED", "RECESO", "ED", "IR", "IR", "MN", "MN", "(MN)"],
            "Jueves": [" ", " ", "RECESO", "SDE", "SDE", "ED", "ED", "PF", "PF"],
            "Viernes": ["SDE", "SDE", "RECESO", "MN", "MN", "IR", "IR", "OE", "(ED)"],
        }
        horario_df = pd.DataFrame(data)
        st.dataframe(horario_df)
        st.write("Las clases entre parentesis ( ) son HTI")

    # Registro de asistencia
    elif choice == "Registrar Asistencia":
        st.subheader("Registrar asistencia de clase")

        # Selección de materia
        materias = obtener_materias()  
        materia_seleccionada = st.selectbox("Seleccionar Materia", materias, format_func=lambda x: x[1])

        # Selección del horario específico
        horarios = ["7:00 - 8:00", "8:00 - 8:40", "8:45 - 9:15", "9:15 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00"]
        hora = st.selectbox("Seleccionar Hora", horarios)

        # Seleccionar la fecha en la que se impartió la clase
        fecha_clase = st.date_input("Seleccionar Fecha", datetime.now())

        # ¿Clase impartida o no?
        impartida = st.radio("¿Clase impartida?", ("Sí", "No"))

        # Registrar asistencia
        if st.button("Registrar Asistencia"):
            registrar_asistencia(materia_seleccionada[0], hora, fecha_clase, impartida == "Sí")
            st.success(f"Asistencia registrada correctamente para {materia_seleccionada[1]} a las {hora}")

    # Generar estadísticas de asistencia
    elif choice == "Generar Estadísticas":
        st.subheader("Generar Estadísticas de Asistencia")
        
        # Selección del tipo de reporte
        tipo_reporte = st.radio("Seleccionar tipo de reporte", ("Por Profesor", "Por Materia", "Global"))
        
        # Si selecciona por profesor, mostrar lista de profesores
        if tipo_reporte == "Por Profesor":
            profesores = obtener_profesores()
            profesor_seleccionado = st.selectbox("Seleccionar Profesor", [(p[0], p[1]) for p in profesores], format_func=lambda x: x[1])
            
            if profesor_seleccionado:
                profesor_id = profesor_seleccionado[0]
                estadisticas, resumen = generar_estadisticas_asistencia_filtrada(tipo_reporte="Por Profesor", profesor_id=profesor_id)
                
                st.subheader(f"Estadísticas para el profesor {profesor_seleccionado[1]}")
                for row in estadisticas:
                    fecha, impartida = row
                    st.write(f"Fecha: {fecha}, Clase Impartida: {'Sí' if impartida == 1 else 'No'}")

                # Mostrar resumen de clases impartidas y no impartidas
                st.write(f"Total de Clases: {resumen['total_clases']}, "
                        f"Clases Impartidas: {resumen['clases_impartidas']}, "
                        f"Clases No Impartidas: {resumen['clases_no_impartidas']}")

        # Si selecciona por materia, mostrar lista de materias
        elif tipo_reporte == "Por Materia":
            materias = obtener_materias()
            materia_seleccionada = st.selectbox("Seleccionar Materia", [(m[0], m[1]) for m in materias], format_func=lambda x: x[1])
            
            if materia_seleccionada:
                materia_id = materia_seleccionada[0]
                estadisticas, resumen = generar_estadisticas_asistencia_filtrada(tipo_reporte="Por Materia", materia_id=materia_id)
                
                st.subheader(f"Estadísticas para la materia {materia_seleccionada[1]}")
                for row in estadisticas:
                    fecha, impartida = row
                    st.write(f"Fecha: {fecha}, Clase Impartida: {'Sí' if impartida == 1 else 'No'}")

                # Mostrar resumen de clases impartidas y no impartidas
                st.write(f"Total de Clases: {resumen['total_clases']}, "
                        f"Clases Impartidas: {resumen['clases_impartidas']}, "
                        f"Clases No Impartidas: {resumen['clases_no_impartidas']}")

        # Global: No requiere selección, simplemente genera estadísticas globales
        else:
            estadisticas, resumen = generar_estadisticas_asistencia_filtrada(tipo_reporte="Global")
            st.subheader("Estadísticas Globales")
            for row in estadisticas:
                fecha, impartida = row
                st.write(f"Fecha: {fecha}, Clase Impartida: {'Sí' if impartida == 1 else 'No'}")

            # Mostrar resumen de clases impartidas y no impartidas
            st.write(f"Total de Clases: {resumen['total_clases']}, "
                    f"Clases Impartidas: {resumen['clases_impartidas']}, "
                    f"Clases No Impartidas: {resumen['clases_no_impartidas']}")
            
    # Agregar/Eliminar maestros y sus materias
    elif choice == "Gestionar Profesores y Materias":
        st.subheader("Gestionar Profesores y Materias")
        
        # Elegir entre crear o eliminar
        accion = st.radio("Seleccionar acción", ("Crear", "Eliminar"))
        
        if accion == "Crear":
            st.write("Crear un nuevo profesor y asignar una materia")

            # Ingresar el nombre del profesor
            nombre_profesor = st.text_input("Nombre del Profesor")

            # Ingresar el nombre de la materia
            nombre_materia = st.text_input("Nombre de la Materia")

            # Botón para crear profesor y materia
            if st.button("Crear Profesor y Materia"):
                if nombre_profesor and nombre_materia:
                    profesor_id = crear_profesor_materia(nombre_profesor, nombre_materia)
                    st.success(f"Se ha creado el profesor '{nombre_profesor}' con la materia '{nombre_materia}'.")
                else:
                    st.error("Por favor ingresa tanto el nombre del profesor como de la materia.")

        elif accion == "Eliminar":
            st.write("Eliminar un profesor y sus materias asociadas")
            
            # Seleccionar profesor a eliminar
            profesores = obtener_profesores()
            profesor_seleccionado = st.selectbox("Seleccionar Profesor a Eliminar", [(p[0], p[1]) for p in profesores], format_func=lambda x: x[1])
            
            if profesor_seleccionado:
                profesor_id = profesor_seleccionado[0]

                # Confirmación antes de eliminar
                if st.button(f"Eliminar al profesor {profesor_seleccionado[1]} y sus materias"):
                    eliminar_profesor_y_materias(profesor_id)
                    st.success(f"Se ha eliminado al profesor '{profesor_seleccionado[1]}' y todas sus materias asociadas.")

    # Exportar asistencias a CSV
    elif choice == "Exportar Asistencias":
        st.subheader("Exportar Asistencias a CSV")
        if st.button("Exportar"):
            exportar_asistencias_a_csv()
            st.success("Asistencias exportadas correctamente a CSV")

if __name__ == '__main__':
    main()
