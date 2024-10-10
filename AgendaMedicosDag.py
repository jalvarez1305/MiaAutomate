# Importar los módulos necesarios
from airflow import DAG
from airflow.operators import PythonOperator
from datetime import datetime, timedelta

# Importa la función SendBlast desde el archivo donde la definiste
from PyLibrary.CW_Automations import SendBlast
from PyLibrary.CW_Conversations import ChatwootSenders

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
    template_name = 'agenda_manana'  # Ajusta el nombre de la plantilla
    buzon = ChatwootSenders.Medico  # Ajusta el buzón según lo que necesites, usando ChatwootSenders.Pacientes
    bot_name = None  # O el nombre del bot, si es necesario
    query = """SELECT        MedicoId,
			  MedicoNickName,
			  'Mañana' as Dia,
			  MIN(FORMAT(start_datetime, 'HH:mm'))  AS Inicio,
			  MAX(FORMAT(start_datetime, 'HH:mm'))  AS Fin
FROM            dbo.vwCalendario
WHERE        (CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1))
GROUP BY MedicoID,MedicoNickName"""  # Ajusta la query a tu necesidad
    
    # Ejecuta SendBlast
    SendBlast(template_name, buzon, bot_name, query)

# Definir la tarea que ejecutará la función
send_blast_task = PythonOperator(
    task_id='send_blast_daily_task',
    python_callable=send_agenda_manana,
    dag=dag,
)

send_blast_task