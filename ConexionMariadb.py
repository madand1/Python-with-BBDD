import mariadb

def conectar_bd():
    """Establece la conexión a la base de datos."""
    try:
        connection = mariadb.connect(
            user='root',
            password='root',
            host='localhost',
            database='basedatoandres'
        )
        cursor = connection.cursor()
        print("Conexión establecida correctamente.")
        return connection, cursor
    except mariadb.Error as error:
        print("Error al conectar a la base de datos:", error)
        return None, None

def cerrar_bd(connection, cursor):
    """Cierra la conexión a la base de datos."""
    try:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Conexión cerrada correctamente.")
    except mariadb.Error as error:
        print("Error al cerrar la conexión a la base de datos:", error)

def obtener_total_profesores(cursor):
    """Obtiene el total de profesores y sus nombres completos."""
    try:
        cursor.execute("""
            SELECT COUNT(*) AS total_profesores, 
                   CONCAT(nombreprofesor, ' ', apellido1, ' ', apellido2) AS nombre_completo
            FROM profesor
            GROUP BY nombreprofesor, apellido1, apellido2
        """)
        resultados = cursor.fetchall()
        print(f"Hay un total de {len(resultados)} profesores:")
        for total_profesores, nombre_completo in resultados:
            print(f"Nombre completo: {nombre_completo}")
    except mariadb.Error as error:
        print("Error al obtener el total de profesores:", error)

def listar_alumnos(cursor):
    """Lista todos los alumnos con sus datos."""
    try:
        cursor.execute("SELECT * FROM alumno")
        alumnos = cursor.fetchall()
        print("Listado de alumnos:")
        for alumno in alumnos:
            id_alumno, nombre, apellido1, apellido2, dni, id_grupo, codigo_postal, id_direccion = alumno
            print(f"ID Alumno: {id_alumno}, Nombre: {nombre}, Apellidos: {apellido1} {apellido2}, DNI: {dni}, ID Grupo: {id_grupo}, Código Postal: {codigo_postal}, ID Dirección: {id_direccion}")
    except mariadb.Error as error:
        print("Error al listar los alumnos:", error)

def obtener_asignaturas_por_profesor(cursor):
    """Obtiene las asignaturas de cada profesor."""
    try:
        cursor.execute("""
           SELECT
    CONCAT(p.nombreprofesor, ' ', p.apellido1, ' ', p.apellido2) AS nombre_completo_profesor,
    a.nombre AS asignatura
FROM profesor p
LEFT JOIN convocatoria cv ON p.id_profesor = cv.id_alumno
LEFT JOIN asignatura a ON cv.id_asignatura = a.id_asignatura
ORDER BY nombre_completo_profesor;

        """)
        resultados = cursor.fetchall()
        asignaturas = {}
        for nombre_completo, asignatura in resultados:
            if nombre_completo not in asignaturas:
                asignaturas[nombre_completo] = []
            asignaturas[nombre_completo].append(asignatura)
        
        for nombre_completo, asignaturas_list in asignaturas.items():
            print(f"\nProfesor: {nombre_completo}")
            print("Asignaturas:")
            if nombre_completo == 'Profesor Sustituto':
                print("Las siguientes asignaturas están a la espera de un profesor sustituto:")
            for asignatura in asignaturas_list:
                print(f"- {asignatura}")
    except mariadb.Error as error:
        print("Error al obtener las asignaturas por profesor:", error)

def listar_alumnos_notas_asignaturas(connection, cursor):
    try:
        # Ejecutar la consulta
        cursor.execute("""
            SELECT a.nombre AS nombre_alumno, a.apellido1, a.apellido2, n.calificacion, asig.nombre AS nombre_asignatura
            FROM alumno a
            INNER JOIN notas n ON a.id_alumno = n.id_alumno
            INNER JOIN asignatura asig ON n.id_asignatura = asig.id_asignatura
        """)
        
        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()
        
        # Mostrar los resultados
        print("Alumnos con sus notas y asignaturas:")
        for nombre_alumno, apellido1, apellido2, calificacion, nombre_asignatura in resultados:
            print(f"Alumno: {nombre_alumno} {apellido1} {apellido2}, Calificación: {calificacion}, Asignatura: {nombre_asignatura}")
    
    except mariadb.Error as error:
        print("Error al ejecutar la consulta:", error)

def actualizar_nota_alumno():
    """Actualiza la nota de un alumno mediante su DNI."""
    
    try:
        connection, cursor = conectar_bd()
        if connection and cursor:
            while True:
                dni = input("Ingrese el DNI del alumno: ")
                cursor.execute("SELECT id_alumno FROM alumno WHERE dni = %s", (dni,))
                resultado = cursor.fetchone()
                if resultado:
                    nueva_nota = float(input("Ingrese la nueva nota: "))  # Cambio aquí para permitir decimales
                    cursor.execute("UPDATE notas SET calificacion = %s WHERE id_alumno = %s", (nueva_nota, resultado[0]))
                    connection.commit()  # Confirmar los cambios en la base de datos
                    print("Nota del alumno actualizada correctamente.")
                    break
                else:
                    print("El DNI ingresado no corresponde a ningún alumno. Intente nuevamente.")

    except mariadb.Error as error:
        print("Error de MariaDB:", error)
    finally:
        cerrar_bd(connection, cursor)

def insertar_alumno(cursor):
    """Inserta un nuevo alumno en la base de datos."""
    try:
        # Solicitar al usuario los datos del alumno
        nombre = input("Ingrese el nombre del nuevo alumno: ")
        apellido1 = input("Ingrese el primer apellido del nuevo alumno: ")
        apellido2 = input("Ingrese el segundo apellido del nuevo alumno: ")
        dni = input("Ingrese el DNI del nuevo alumno: ")
        id_grupo = input("Ingrese el ID del grupo del nuevo alumno: ")
        codigo_postal = input("Ingrese el código postal del nuevo alumno: ")
        id_direccion = input("Ingrese el ID de la dirección del nuevo alumno: ")
        
        # Verificar si el ID del alumno ya existe en la tabla
        cursor.execute("SELECT MAX(id_alumno) FROM alumno")
        ultimo_id = cursor.fetchone()[0]
        id_alumno = ultimo_id + 1 if ultimo_id is not None else 1
        
        # Insertar el alumno
        cursor.execute("INSERT INTO alumno (id_alumno, nombre, apellido1, apellido2, dni, id_grupo, codigo_postal, id_direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id_alumno, nombre, apellido1, apellido2, dni, id_grupo, codigo_postal, id_direccion))
        cursor.connection.commit()
        print("Alumno insertado correctamente.")
    except mariadb.Error as error:
        print("Error al insertar el alumno:", error)

def eliminar_alumno_por_dni(cursor):
    """Elimina un alumno por su número de identificación (DNI)."""
    try:
        for intento in range(3):
            dni = input("Ingrese el DNI del alumno que desea eliminar: ")
            cursor.execute("SELECT COUNT(*) FROM alumno WHERE dni = %s", (dni,))
            cantidad_alumnos = cursor.fetchone()[0]
            if cantidad_alumnos == 0:
                print("No se encontró ningún alumno con el DNI proporcionado.")
            else:
                cursor.execute("DELETE FROM alumno WHERE dni = %s", (dni,))
                cursor.connection.commit()
                print("Alumno eliminado correctamente.")
                break
        else:
            print("Se agotaron los intentos. No se pudo eliminar al alumno.")
    except mariadb.Error as error:
        print("Error al eliminar el alumno:", error)

def mostrar_menu():
    """Muestra el menú de opciones."""
    print("\nMenú:")
    print("1. Mostrar total de profesores.")
    print("2. Mostrar lista de todos los alumnos")
    print("3. Mostrar asignaturas por profesor.")
    print("4. Listar alumnos con sus notas y asignaturas.")
    print("5. Actualizar nota de un alumno.")
    print("6. Incorporación de nuevo alumno.")
    print("7. Dar de baja a un alumno.")
    print("8. Salir.")

def main():
    """Función principal."""
    try:
        connection, cursor = conectar_bd()
        if connection and cursor:
            while True:
                mostrar_menu()
                opcion = input("Seleccione una opción: ")
                if opcion == "1":
                    obtener_total_profesores(cursor)
                elif opcion == "2":
                    listar_alumnos(cursor)
                elif opcion == "3":
                    obtener_asignaturas_por_profesor(cursor)
                elif opcion == "4":
                    listar_alumnos_notas_asignaturas(connection, cursor)
                elif opcion == "5":
                    actualizar_nota_alumno()
                elif opcion == "6":
                    insertar_alumno(cursor)
                elif opcion == "7":
                    eliminar_alumno_por_dni(cursor)
                elif opcion == "8":
                    print("Saliendo del programa...")
                    break
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
    except mariadb.Error as error:
        print("Error de MariaDB:", error)
    finally:
        cerrar_bd(connection, cursor)

if __name__ == "__main__":
    main()
