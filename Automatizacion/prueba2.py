from datetime import datetime
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import os
db_config = {
    'host': '10.10.0.251',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'hhrr_dev',
}

connection = pymysql.connect(**db_config)

def enviar_correo(destinatatio=[], msg=""):
    remitente = "jzuniga@plena.global"
    destinatario = destinatatio
    password = "JsZuniga*2250"

    server = smtplib.SMTP("smtp-mail.outlook.com", 587)
    server.starttls()
    server.login(remitente, password)

    body = f"""
        <div>
        Cordial Saludo,
        </br>
        </br>
        {msg}
        </br>
        </br>
        Atentamente,
        </br>
        </br>
        Recursos Humanos
        </div>
        </br>
        <img src="cid:footer_image">
        """
    msg = MIMEMultipart()
    msg["Subject"] = "Evaluación periodo de prueba"
    msg["From"] = remitente
    msg["To"] = destinatario

    msg.attach(MIMEText(body, "html"))

    script_directory = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_directory, "logo2.png")

    # Adjuntar la imagen del footer al mensaje
    with open(image_path, "rb") as image_file:
        footer_image = MIMEImage(image_file.read())
        footer_image.add_header("Content-ID", "<footer_image>")
        msg.attach(footer_image)

    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()



def warning_email():
    print("warning ajecutado")
    date_current = datetime.now()
    with connection.cursor() as cursor:
        query = """
            SELECT * FROM tbl_trial_time_evaluation WHERE ccn_order_state != %s AND ccn_order_state !=%s;
        """
        cursor.execute(query, (5,6))
        trian_time_evaluations = cursor.fetchall()

        for tte in trian_time_evaluations:
            if tte[4] == 1:
                difference = date_current - tte[7]
                if difference.days >=1:
                    print("entre estado 1")
                    query = """
                        SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_trial_time_evaluation tte
                            JOIN tbl_employment_relationship emr
                            ON emr.ccn_employee = tte.ccn_evaluator
                            JOIN tbl_employee emp
                            ON emp.ccn_employee = tte.ccn_evaluator
                            WHERE tte.ccn_trial_time_evaluation = %s
                        """
                    cursor.execute(query, tte[0])
                    evaluator = cursor.fetchone()

                    query = """
                        SELECT full_name_employee FROM tbl_employee WHERE ccn_employee = %s;
                        """
                    cursor.execute(query, tte[1])
                    colaborator = cursor.fetchone()

                    message = f"""
                    {evaluator[2]}, mediante la presente se recuerda que tiene pendiente la evaluación de periodo de prueba del colaborador {colaborator[0]}.
                    </br>
                    Para evaluar al colaborador, haga clic en el siguiente enlace: https://hhrr.plena-global.com/
                    """
                    if evaluator[0] and evaluator[0] != "NO@NO.COM":
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)
                    else:
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)

            elif tte[4] == 2:
                difference = date_current - tte[6]
                if difference.days >=1:
                    print("entre estado 2")
                    query = """
                        SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_trial_time_evaluation tte
                            JOIN tbl_employment_relationship emr
                            ON emr.ccn_employee = tte.ccn_employee
                            JOIN tbl_employee emp
                            ON emp.ccn_employee = tte.ccn_employee
                            WHERE tte.ccn_trial_time_evaluation = %s
                        """
                    cursor.execute(query, tte[0])
                    colaborator = cursor.fetchone()

                    message = f"""
                        {colaborator[2]}, mediante la presente se recurda que esta pendiente su respuesta sobre la calificación en la evaluación de periodo de prueba.
                        </br>
                        Para dar su apreciación sobre esta, haga clic en el siguiente enlace: https://hhrr.plena-global.com/
                    """
                    if colaborator[0] and colaborator[0] != "NO@NO.COM":
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)
                    else:
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)

            elif tte[4] == 4:
                difference = date_current - tte[5]
                print("entre estado 4")
                if difference.days >=1:
                    query = """
                        SELECT emr.employee_corporate_email, emp.employee_personal_email, emp.full_name_employee FROM tbl_trial_time_evaluation tte
                            JOIN tbl_employment_relationship emr
                            ON emr.ccn_employee = tte.manager_hhrr
                            JOIN tbl_employee emp
                            ON emp.ccn_employee = tte.manager_hhrr
                            WHERE tte.ccn_trial_time_evaluation = %s
                        """
                    cursor.execute(query, tte[0])
                    manager = cursor.fetchone()

                    query = """
                        SELECT full_name_employee FROM tbl_employee WHERE ccn_employee = %s;
                        """
                    cursor.execute(query, tte[1])
                    colaborator = cursor.fetchone()

                    message = f"""
                        Mediante la presente se recuerda que la evaluación de periodo de prueba del colaborador {colaborator[0]} esta pendiente por aprobación.
                        </br>
                        Para aprobar o desaprobar la evaluación, haga clic en el siguiente enlace: https://hhrr.plena-global.com/
                    """
                    if manager[0] and manager[0] != "NO@NO.COM":
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)
                    else:
                        enviar_correo("jhonsebastian2250@gmail.com", msg=message)
            else: return

# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(warning_email, 'cron', hour=8, minute=55, timezone="America/Bogota")
#     scheduler.start()

#     try:
#         while True:
#             pass
#     except (KeyboardInterrupt, SystemExit):
#         scheduler.shutdown()
#         connection.close()
            
warning_email()