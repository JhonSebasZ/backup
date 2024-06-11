import pymysql
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, date, datetime
from automatizacion import enviar_correo

# Configuración de la conexión a la base de datos
db_config = {
    'host': '10.10.0.251',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'hhrr_pro',
}

connection = pymysql.connect(**db_config)


def calcular_dias_vinculacion(fecha_vinculacion):
    return (datetime.now() - fecha_vinculacion).days


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


def execute_query2(query, params=None):
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()

            # Devuelve los resultados después de ejecutar la consulta
            return cursor.fetchall()
    except Exception as e:
        connection.rollback()
        raise e


def performance_evaluation():
    fecha_limite = date(
        date.today().year - 1, 9, 30
    )  # Fecha límite para la comparación

    date_current = date.today()

    count_register = 0

    with connection.cursor() as cursor:
        """
        Esta query trae a los colaboradores que cumplan las siguientes condiciones:
            1. El colaborador debe de estar activo?
            2. La fecha de vinculación debe de ser menor a el 30 de septiembre del año inmediatamente anterior
            3. El colaborador debe de tener un ccn diferente a 0
            4. La realcion del colaborador debe de ser diferente a Pasante SENA o Pasante Universitario
            5. El colaborador debe de llevar mas de 60 dias en la compañia
            6. El campo de la fecha de terminacion de contrato debe de estar en NULL
        """
        query = """
        SELECT empr.ccn_employee, empr.immediate_boss, empr.manager, empr.type_of_charge
            FROM tbl_employment_relationship empr
            JOIN tbl_employee emp ON emp.ccn_employee = empr.ccn_employee
            WHERE is_active_employee = %s
                AND empr.binding_date <= %s 
                AND emp.ccn_employee <> %s
                AND empr.ccn_type_relationship NOT IN (%s, %s)
                AND DATEDIFF(%s, empr.binding_date) > %s
                AND empr.termination_date is NULL
                ORDER BY emp.full_name_employee
        """
        params = (1, fecha_limite, 0, 9, 10, date_current, 60)
        employees = execute_query2(query, params)

        """
        emp[0] = ccn_employee
        emp[1] = immediate_boss
        emp[2] = manager
        emp[3] = type_of_charge
        """
        for emp in employees:
            if (emp[1] == 0):
                continue

            PE = """
            SELECT ccn_performance_evaluation, opening_date, ccn_employee
            FROM tbl_performance_evaluation WHERE ccn_employee = %s ORDER BY opening_date DESC
            LIMIT 1            
            """
            params = (emp[0])
            PEE = execute_query2(PE, params)

            if len(PEE) == 0:
                try:
                    create_evaluation(emp[1], emp[2], emp[0], emp[3])
                    count_register = count_register + 1
                except:
                    print(
                        "error creando la evaluacion del colaborador", emp[0])

            else:
                if date.today().year != PEE[0][1].year:
                    try:
                        create_evaluation(emp[1], emp[2], emp[0], emp[3])
                        print(emp)
                        count_register = count_register + 1
                    except:
                        print(
                            "error creando la evaluacion del colaborador", emp[0])
        print("Se han insertados", count_register, "registros")


def create_evaluation(ccn_inmediate_boss, ccn_manager, ccn_employee, type_employee):

    with connection.cursor() as cursor:
        inmediate_boss = cursor.execute(
            """
                                SELECT empr.*, emp.employee_personal_email, emp.full_name_employee FROM tbl_employment_relationship  empr
                                JOIN tbl_employee emp 
                                ON emp.ccn_employee = empr.ccn_employee
                                WHERE empr.ccn_employee = %s
                            """,
            ccn_inmediate_boss
        )
        inmediate_boss = cursor.fetchone()

        if (calcular_dias_vinculacion(inmediate_boss[4]) > 60):
            queries(ccn_inmediate_boss, ccn_manager,
                    ccn_employee, type_employee)

        else:
            queries(ccn_manager, ccn_manager, ccn_employee, type_employee)


def queries(ccn_inmediate_boss, ccn_manager, ccn_employee, type_employee):
    with connection.cursor() as cursor:
        query = """
                    INSERT INTO tbl_performance_evaluation (opening_date, immediate_boss, manager, ccn_employee, type_employee, ccn_states_performance_evaluation) 
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
        execute_query(query, (datetime.now(), ccn_inmediate_boss,
                      ccn_manager, ccn_employee, type_employee, 1))

        # Optiene la ultima fila insertada
        cursor.execute("SELECT LAST_INSERT_ID()")
        PE_id = cursor.fetchone()[0]

        if type_employee == "ADMINISTRATIVO":
            query = """
                INSERT INTO tbl_administrative_performance_evaluation (ccn_performance_evaluation, ccn_employee) 
                VALUES (%s, %s);
            """
            execute_query(query, (PE_id, ccn_employee))

        elif type_employee == "OPERATIVO":
            query = """
                INSERT INTO tbl_operative_performance_evaluation (ccn_performance_evaluation, ccn_employee) 
                VALUES (%s, %s);
            """
            execute_query(query, (PE_id, ccn_employee))

        elif type_employee == "DIRECTIVO":
            query = """
                INSERT INTO tbl_directive_performance_evaluation (ccn_performance_evaluation, ccn_employee) 
                VALUES (%s, %s);
            """
            execute_query(query, (PE_id, ccn_employee))

        query1 = """
            SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_employee emp
                JOIN tbl_employment_relationship emr
                ON emr.ccn_employee = emp.ccn_employee
                WHERE emp.ccn_employee = %s
            """
        cursor.execute(query1, ccn_inmediate_boss)
        inmediate_boss = cursor.fetchone()

        query2 = """
            SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_employee emp
                JOIN tbl_employment_relationship emr
                ON emr.ccn_employee = emp.ccn_employee
                WHERE emp.ccn_employee = %s
            """
        cursor.execute(query2, ccn_manager)
        manger = cursor.fetchone()

        query3 = """
            SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_employee emp
                JOIN tbl_employment_relationship emr
                ON emr.ccn_employee = emp.ccn_employee
                WHERE emp.ccn_employee = %s
            """
        cursor.execute(query3, ccn_employee)
        employee = cursor.fetchone()
        cursor.close()

        print(inmediate_boss)
        print(manger)
        print(employee)

        try:
            email_employee = employee[0] if employee[0] and employee[0] != "NO@NO.COM" else employee[1]
            email_evaluator = inmediate_boss[0] if inmediate_boss[0] and inmediate_boss[0] != "NO@NO.COM" else inmediate_boss[1]
            enviar_correo(destinatatio=[email_employee, email_evaluator],
                          name_evaluator=inmediate_boss[2], name_colaborator=employee[2])
        except Exception as ex:
            print("Error al enviar el correo", ex)


# performance_evaluation()

performance_evaluation()
