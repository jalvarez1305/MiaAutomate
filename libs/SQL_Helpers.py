import pymssql
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Obtener las variables de conexión desde el archivo .env
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

def GetParametersFromQuery(query):
    """
    Ejecuta una consulta SQL y devuelve los valores de la primera fila como una lista.

    :param query: El query SQL a ejecutar.
    :return: Una lista con los valores de cada columna de la primera fila del resultado o None si no se encuentra ninguna fila.
    :raises Exception: Si ocurre un error durante la ejecución del query.
    """
    try:
        # Ejecutar la consulta y obtener el resultado (solo la primera fila)
        result = execute_query(query)

        # Verificar si el resultado existe y tiene datos
        if result is not None and not result.empty:
            # Acceder a la primera fila y convertir los valores a una lista
            parametros = [str(param) if param is not None else '' for param in result.iloc[0]]
            return parametros
        else:
            return None  # Devolver None si no se encuentra ninguna fila

    except Exception as e:
        # Registrar el error para debugging
        print(f"Error ejecutando la consulta: {e}")
        raise  # Propagar la excepción para manejo externo

def GetTemplateDetails(template_sid):
    """
    Obtiene los detalles de una plantilla desde la base de datos por su nombre.
    
    :param template_name: El nombre de la plantilla a buscar.
    :return: Un diccionario con los detalles de la plantilla (Name, Body, sid, url) o None si no se encuentra.
    """
    # Consulta SQL para obtener los detalles de la plantilla
    query = f"""
    SELECT TOP 1 
           [Name],
           [Body],
           [sid],
           [url]
      FROM [cfg].[WS_Templates]
     WHERE [sid] = '{template_sid}'
    """
    
    # Ejecutar la consulta y obtener el resultado
    result = execute_query(query)
    
    # Verificar si el resultado existe y tiene datos
    if result is not None and not result.empty:
        return {
            'Name': result.iloc[0]['Name'],
            'Body': result.iloc[0]['Body'],
            'sid': result.iloc[0]['sid'],
            'url': result.iloc[0]['url']
        }
    else:
        return None

def execute_query(query):
    """
    Ejecuta una consulta SQL y devuelve un DataFrame si el resultado es una tabla,
    o None si no hay resultados tabulares.
    
    :param query: La consulta SQL a ejecutar.
    :return: Un DataFrame con los resultados o None si el resultado no es una tabla.
    """
    try:
        # Establecer la conexión a la base de datos usando pymssql
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        
        # Ejecutar la consulta SQL y cargar los resultados en un DataFrame
        df = pd.read_sql(query, conn)
        
        # Verificar si el DataFrame tiene contenido
        if df.empty:
            return None
        else:
            return df
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None
    finally:
        # Cerrar la conexión
        conn.close()
def GetFreeTime(Consultorio=6):
    """
    Obtiene el tiempo libre de un consultorio específico desde la base de datos.

    :param Consultorio: El ID del consultorio a consultar (por defecto es 6).
    :return: Un texto completo con loshorarios disponibles o None si no hay resultados.
    """
    #Consulta para saber el siguiente día habil
    query = f"""select Top 1 Fecha, 
                        case when 
                                DATEDIFF(dd,GETDATE(),Fecha) <=1 then 'Mañana'
                                else Name
                            End as Dia
            from [cfg].[Calendario]
            where is_habil=1 and Fecha > GETDATE()
            """
    # Ejecutar la consulta y obtener el resultado
    result_siguiente_dia = execute_query(query)
    #consulta para obtener sicuiente cita matutina
    query_matutina = f"""EXEC sp_BuscarPrimerEspacioDisponible '{result_siguiente_dia.iloc[0]['Fecha']}'"""
    #Obtener la siguiente libre de turno matutino
    matutino=execute_query(query_matutina)

    #consulta para obtener sicuiente cita vespertino
    query_vespertino = f"""EXEC sp_BuscarPrimerEspacioVespertino '{result_siguiente_dia.iloc[0]['Fecha']}'"""
    #Obtener la siguiente libre de turno matutino
    vespertino=execute_query(query_vespertino)

    #Construye el texto    
    
    # Verificar si el resultado existe y tiene datos
    if (matutino is not None and not matutino.empty) or (vespertino is not None and not vespertino.empty):
        result = f"{result_siguiente_dia.iloc[0]['Dia']} tengo varios espacios, como por ejemplo "
        if (matutino is not None and not matutino.empty):
            result += f" {matutino.iloc[0]['libre']} "
            if (vespertino is not None and not vespertino.empty):
                result += f" y {vespertino.iloc[0]['libre']}."
        else:
            if (vespertino is not None and not vespertino.empty):
                result += f" {vespertino.iloc[0]['libre']}."
        result += f"\nQue horario tenias en mente?"
        return result
    else:
        return None
    
    
def ExecuteScalar(query):
    """
    Ejecuta una consulta SQL que retorna un solo valor y devuelve ese valor como string,
    o None si no hay un resultado o si ocurre un error. También permite ejecutar consultas
    que no devuelvan ningún resultado, como actualizaciones, eliminaciones o ejecuciones de procedimientos almacenados.

    :param query: La consulta SQL a ejecutar.
    :return: Un string con el valor devuelto por la consulta, None si no hay resultados,
             o None en caso de consultas de tipo UPDATE, INSERT, DELETE o EXEC.
    """
    try:
        # Establecer la conexión a la base de datos
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        
        # Crear un cursor y ejecutar la consulta
        with conn.cursor() as cursor:
            cursor.execute(query)

            # Si la consulta es de lectura (SELECT), obtener el primer resultado
            if query.strip().lower().startswith("select"):
                result = cursor.fetchone()
                return str(result[0]) if result else None
            else:
                # Hacer commit explícito para consultas de escritura o ejecución de procedimientos (EXEC)
                conn.commit()
                return None  # No hay un valor para devolver en consultas de escritura o procedimientos
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None
    finally:
        # Cerrar la conexión
        conn.close()

def ejecutar_update(query):
    """
    Ejecuta una consulta de actualización en SQL Server.

    :param query: La consulta SQL de tipo UPDATE, INSERT o DELETE.
    """
    conn = None
    cursor = None
    try:
        print("Conectando a la base de datos...")
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()
        print("Conexión establecida.")

        print(f"Ejecutando query: {query}")
        cursor.execute(query)
        conn.commit()
        
        print("Actualización realizada exitosamente.")
        
    except pymssql.DatabaseError as db_err:
        print(f"❌ Error de base de datos: {db_err}")
        if conn:
            conn.rollback()  # Revertir cambios en caso de error

    except pymssql.InterfaceError as conn_err:
        print(f"❌ Error de conexión: {conn_err}")

    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión cerrada.")