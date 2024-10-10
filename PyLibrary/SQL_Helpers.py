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

def get_template_body(template_name):
    """
    Obtiene el cuerpo de una plantilla desde la base de datos por su nombre.
    
    :param template_name: El nombre de la plantilla a buscar.
    :return: El contenido del body de la plantilla o None si no se encuentra.
    """
    # Consulta SQL para obtener el Body de la plantilla
    query = f"""
    SELECT [Body]
    FROM [cfg].[WS_Templates]
    WHERE [name] = '{template_name}'
    """
    
    # Ejecutar la consulta y obtener el resultado
    result = execute_query(query)
    
    # Verificar si el resultado existe y tiene un body
    if result is not None and not result.empty:
        return result.iloc[0]['Body']
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
