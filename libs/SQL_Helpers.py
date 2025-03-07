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
    try:
        # Establece la conexión
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()
        
        # Ejecuta el query
        cursor.execute(query)
        
        # Confirma los cambios
        conn.commit()
        print("Actualización realizada exitosamente.")
        
    except Exception as e:
        print("Error al ejecutar el query:", e)
        
    finally:
        # Cierra la conexión
        cursor.close()
        conn.close()