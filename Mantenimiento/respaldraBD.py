import os
import logging
from datetime import datetime
import boto3
import pymssql
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_SERVER = os.getenv('SQL_SERVER')
DB_NAME = os.getenv('DB_NAME', 'clinica')
DB_USER = os.getenv('SQL_USERNAME')
DB_PASSWORD = os.getenv('SQL_PASSWORD')

# Configuración de AWS S3
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET_NAME = "bd-backups-mia"
S3_BACKUP_FOLDER = ""

# Ruta donde SQL Server tiene permisos de escritura
SQL_BACKUP_DIR = "/var/opt/mssql/data"  # Asegúrate de que SQL Server tenga permisos ahí

def respaldar_base_datos():
    """Realiza el respaldo de la base de datos SQL Server"""
    try:
        fecha_respaldo = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f"{DB_NAME}_backup_{fecha_respaldo}.bak"
        backup_file = os.path.join(SQL_BACKUP_DIR, backup_filename)

        logging.info(f"Iniciando conexión a SQL Server en {DB_SERVER}")
        conn = pymssql.connect(
            server=DB_SERVER,
            user=DB_USER,
            password=DB_PASSWORD,
            database='master',
            autocommit=True
        )

        cursor = conn.cursor()
        logging.info(f"Realizando respaldo a {backup_file}")

        query = f"""
        BACKUP DATABASE [{DB_NAME}]
        TO DISK = N'{backup_file}'
        WITH NOFORMAT, INIT, NAME = N'{DB_NAME}-Full Backup', SKIP, STATS = 10
        """

        cursor.execute(query)
        logging.info(f"Respaldo completado exitosamente")
        return backup_file

    except Exception as e:
        logging.error(f"Error al respaldar la base de datos: {e}")
        return None

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def subir_a_s3(backup_file):
    """Sube el archivo de respaldo a un bucket de S3"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )

        s3_key = os.path.join(S3_BACKUP_FOLDER, os.path.basename(backup_file))
        logging.info(f"Subiendo respaldo a S3: s3://{S3_BUCKET_NAME}/{s3_key}")
        s3_client.upload_file(backup_file, S3_BUCKET_NAME, s3_key)

        logging.info("Respaldo subido correctamente a S3.")
    except Exception as e:
        logging.error(f"Error al subir el respaldo a S3: {e}")

def eliminar_respaldo_local(backup_file):
    """Elimina el respaldo local para ahorrar espacio"""
    try:
        os.remove(backup_file)
        logging.info(f"Archivo local eliminado: {backup_file}")
    except Exception as e:
        logging.warning(f"No se pudo eliminar el archivo local: {e}")

def main():
    backup_file = respaldar_base_datos()
    if backup_file:
        subir_a_s3(backup_file)
        eliminar_respaldo_local(backup_file)

if __name__ == "__main__":
    main()
