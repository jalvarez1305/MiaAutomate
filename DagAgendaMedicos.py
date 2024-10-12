# Importar los módulos necesarios
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/root/airflow/dags/libs')
# Importa la función SendBlast desde el archivo donde la definiste
from libs.CW_Automations import SendBlast
from libs.CW_Conversations import ChatwootSenders

# Definir los parámetros de la DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 10),  # Fecha en la que el DAG empieza
    'retries': 1,  # Número de intentos de reintento en caso de fallo
    'retry_delay': timedelta(minutes=5),  # Tiempo entre intentos
    'catchup': False,  # Si es False, no ejecutará las tareas que quedaron pendientes antes de la fecha de start_date
}

# Definir el DAG
dag = DAG(
    'send_blast_daily',
    default_args=default_args,
    description='DAG para enviar blast diarios usando SendBlast',
    schedule_interval='0 8 * * *',  # Ejecutar todos los días a las 8 a.m.
    catchup=False,
)

# Función que ejecuta SendBlast
def send_agenda_manana():
    template_name = 'agenda_sumary2'
    buzon = ChatwootSenders.Medicos  # Instancia de la clase ChatwootSenders
    bot_name = 'AgendaMedico'  # Si no deseas usar un bot, puedes pasar None
    query = """SELECT 162 as ContactID,'Pablo' Nombre,'Mañana' Dia,'13:20' Inicio,'14:19' Fin"""

    SendBlast(template_name, buzon, bot_name, query)
# Definir la tarea que ejecutará la función
send_blast_task = PythonOperator(
    task_id='send_blast_daily_task',
    python_callable=send_agenda_manana,
    dag=dag,
)

send_blast_task