import pymysql
import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, date, datetime
# from connection_db import connection, execute_query
# from send_email_evaluator import enviar_correo

# Configuración de la conexión a la base de datos
db_config = {
    'host': '10.10.0.251',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'hhrr_pro'
}

connection = pymysql.connect(**db_config)

def execute_query(query, params=None):
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

def calcular_dias_vinculacion(fecha_vinculacion):
    return (datetime.now() - fecha_vinculacion).days



def trial_time_evaluation():
    print("test ejecutado")
    evaluations_time = datetime.now() - timedelta(days=200)

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT empr.ccn_employee,empr.binding_date,empr.ccn_type_relationship,empr.immediate_boss,empr.manager, empr.employee_corporate_email, temp.employee_personal_email, temp.full_name_employee FROM tbl_employment_relationship empr
            JOIN tbl_employee temp
            ON temp.ccn_employee = empr.ccn_employee
            WHERE empr.binding_date >= %s
            """
            cursor.execute(query, evaluations_time)
            employees = cursor.fetchall()

            query_history = """ SELECT th.ccn_employee,th.initial_date,th.ccn_type_relationship,th.ccn_inmediate_boss,th.ccn_manager, th.ccn_last_role, empr.employee_corporate_email, temp.employee_personal_email, temp.full_name_employee  FROM tbl_history th
                                JOIN tbl_employment_relationship empr
                                ON empr.ccn_employee = th.ccn_employee
                                JOIN tbl_employee temp
                                ON temp.ccn_employee = th.ccn_employee
                                WHERE final_date IS null;"""
            cursor.execute(query_history, )
            histories = cursor.fetchall()

            employees_for_Evaluation = list()

            for employee in employees:
                emp = {
                    "ccn_employee":employee[0],
                    "binding_date":employee[1],
                    "ccn_type_relationship":employee[2],
                    "inmediate_boss":employee[3],
                    "manager":employee[4],
                    "email": employee[5] if employee[5] and employee[5] != "NO@NO.COM" else employee[6],
                    "full_name": employee[7]
                }
                employees_for_Evaluation.append(emp)

            for history in histories:
                if calcular_dias_vinculacion(history[1]) == 50 and history[5] != None:
                    emp = {
                        "ccn_employee":history[0],
                        "binding_date":history[1],
                        "ccn_type_relationship":history[2],
                        "inmediate_boss":history[3],
                        "manager":history[4],
                        "email": employee[5] if employee[5] and employee[5] != "NO@NO.COM" else employee[6],
                        "full_name": employee[7]
                    }
                    employees_for_Evaluation.append(emp)
            
            print(employees_for_Evaluation)
            print(datetime.now())

            for employee in employees_for_Evaluation:
                inmediate_boss = cursor.execute(
                        """
                            SELECT empr.*, emp.employee_personal_email, emp.full_name_employee FROM tbl_employment_relationship  empr
                            JOIN tbl_employee emp 
                            ON emp.ccn_employee = empr.ccn_employee
                            WHERE empr.ccn_employee = %s
                        """,
                        employee["inmediate_boss"]
                    )
                # employee[11] : jefe inmediato del colaborador
                inmediate_boss = cursor.fetchone()
                
                # employee["ccn_type_relationship"] == 1 : El colaborador tiene vinculacion directa?
                # employee["binding_date"] == 50: El colaborador lleva 50 dias en la compañia?
                
                if (employee["ccn_type_relationship"] == 1 and calcular_dias_vinculacion(employee["binding_date"]) == 50):

                    # inmediate_boss[4]) > 60 : El jefe inmediato lleva mas de 60 dias?
                    if (calcular_dias_vinculacion(inmediate_boss[4]) > 60):
                        try:
                            execute_query(
                                """
                                INSERT INTO tbl_trial_time_evaluation (ccn_employee, ccn_evaluator, ccn_order_state, created_date, creator, manager_hhrr)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (employee["ccn_employee"], inmediate_boss[1], 1, datetime.now(), "RECURSOS HUMANOS",3))
                            
                            # Optiene la ultima fila insertada
                            cursor.execute("SELECT LAST_INSERT_ID()")
                            trial_time_evaluation_id = cursor.fetchone()[0]
                            execute_query(
                                """
                                INSERT INTO tbl_trial_time_evaluation_detail (ccn_trial_time_evaluation)
                                VALUES (%s)
                                """,
                                (trial_time_evaluation_id,),
                            )
                        except Exception as e:
                            print(f"Error en test - linea 126: {e} {employee}")
                            connection.rollback()
                            continue
                        # if inmediate_boss[9] and inmediate_boss[9] != "NO@NO.COM":
                        #     enviar_correo([inmediate_boss[9]], inmediate_boss[17], employee["full_name"])
                        # else:
                        #     enviar_correo([inmediate_boss[16]], inmediate_boss[17], employee["full_name"])
                    else:
                        try:
                            execute_query(
                                """
                                INSERT INTO tbl_trial_time_evaluation (ccn_employee, ccn_evaluator, ccn_order_state, created_date, creator, manager_hhrr)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (employee["ccn_employee"], employee["manager"], 1, datetime.now(), "RECURSOS HUMANOS", 3),
                            )
                            
                            # employee[12]: manager del colaborador

                            # Optiene la ultima fila insertada
                            cursor.execute("SELECT LAST_INSERT_ID()")
                            trial_time_evaluation_id = cursor.fetchone()[0]
                            execute_query(
                                """
                                INSERT INTO tbl_trial_time_evaluation_detail (ccn_trial_time_evaluation)
                                VALUES (%s)
                                """,
                                (trial_time_evaluation_id,),
                            )
                        except Exception as e:
                            print(f"Error en test - 156: {e} {employee}")
                            connection.rollback()
                            continue
                        # if inmediate_boss[9] and inmediate_boss[9] != "NO@NO.COM":
                        #     enviar_correo([inmediate_boss[9]], inmediate_boss[17], employee["full_name"])
                        # else:
                        #     enviar_correo([inmediate_boss[16]], inmediate_boss[17], employee["full_name"])
                    
                # employee[8] == 9 or employee[8] == 10 : El colaborador es aprendiz sena o universitario, y lleva 170 dias en la empresa?
                elif ((employee["ccn_type_relationship"] == 9 or employee["ccn_type_relationship"] == 10) and calcular_dias_vinculacion(employee["binding_date"]) == 170):
                    try:
                        execute_query(
                            """
                            INSERT INTO tbl_trial_time_evaluation (ccn_employee, ccn_evaluator, ccn_order_state, created_date, creator, manager_hhrr)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (employee["ccn_employee"], employee["manager"], 1, datetime.now(), "RECURSOS HUMANOS",3),
                        )
                        # Optiene la ultima fila insertada
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        trial_time_evaluation_id = cursor.fetchone()[0]
                        execute_query(
                            """
                            INSERT INTO tbl_trial_time_evaluation_detail (ccn_trial_time_evaluation)
                            VALUES (%s)
                            """,
                            (trial_time_evaluation_id,),
                        )
                    except Exception as e:
                        print(f"Error en test - linea 185: {e} {employee}")
                        connection.rollback()
                        continue
                    # if inmediate_boss[9] and inmediate_boss[9] != "NO@NO.COM":
                    #     enviar_correo([inmediate_boss[9]], inmediate_boss[17], employee["full_name"])
                    # else:
                    #     enviar_correo([inmediate_boss[16]], inmediate_boss[17], employee["full_name"])
                else:
                    print(f"No hay evaluaciones pendientes: {datetime.now()}")
    except Exception as e:
        print(f"Error en test: {e}")

trial_time_evaluation()


# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(trial_time_evaluation, 'cron', hour=5, minute=00, timezone="America/Bogota")
#     scheduler.start()

#     # Mantener el script en ejecución
#     try:
#         while True:
#             pass
#     except (KeyboardInterrupt, SystemExit):
#         # Detener el planificador antes de salir
#         scheduler.shutdown()
#         connection.close()