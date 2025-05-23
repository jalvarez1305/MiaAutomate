

from AI.OpenIAHelper import get_requested_date
from libs.SQL_Helpers import GetFreeTimeForDate


msg_arr=[{
                "role": "user",
                "content": "Mañana no podría sería el sig viernes que descanso",
                "created_at": "2023-10-01T12:00:00Z",
            }]
fecha_solicitada=get_requested_date(msg_arr)
horarios = GetFreeTimeForDate(fecha_solicitada,Consultorio=6)
print(f"Revisando la fecha {fecha_solicitada}")
print(horarios)