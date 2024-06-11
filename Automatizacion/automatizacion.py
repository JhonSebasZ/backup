import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def enviar_correo(destinatatio=[], name_evaluator=None, name_colaborator=None, name_manager=None, state=1):
    remitente = "support@plena.global"
    destinatario = destinatatio
    password = "PlenaGlobal2023*"
    destinatario.append("dneira@plena.global")
    destinatario.append("lorjuela@plena.global")
    nombre_de_host = socket.gethostname()
    try:
        try:
            server = smtplib.SMTP("smtp-mail.outlook.com", "587")
            server.ehlo(nombre_de_host.lower())
            server.starttls()
            server.ehlo(nombre_de_host.lower()) 
            server.login(remitente, password)
        except Exception as ex:
            print(ex)
        message = f"""
            {name_evaluator}, mediante la presente se informa que se ha generado la evaluación de desempeño del colaborador {name_colaborator}.
            </br>
            Para evaluar al colaborador, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """

        if state == 2:
            message = f"""
            {name_colaborator}, mediante la presente se informa que se ha realizado la calificación de su evaluación de desempeño.
            </br>
            Para dar su apreciación sobre esta, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """
        
        if state == 3:
            message = f"""
            {name_evaluator}, mediante la presente se informa que el colaborador {name_colaborator} se encuentra pendiente por asignación de plan de acción.
            </br>
            Para definir el plan de acción, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """
        
        if state == 4:
            message = f"""
            {name_manager}, Mediante la presente se informa que la evaluación de desempeño del colaborador {name_colaborator} esta pendiente por aprobación.
            </br>
            Para aprobar o desaprobar, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """
            
        if state == 5:
            message = f"""
            Mediante la presente se informa que la evaluación de desempeño del colaborador {name_colaborator} ha sido finalizada.
            </br>
            Para ver los detalles de la evaluación, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """

        if state == 6:
            print(state)
            message = f"""
            Mediante la presente se informa que la evaluación de desempeño del colaborador {name_colaborator} ha sido rechazada.
            </br>
            Para ver los detalles, haga clic en el siguiente enlace: <a href="https://hhrr.plena-global.com/">https://hhrr.plena-global.com/<a/>
            </br>
        """

        body = f"""
            <div>
            Cordial Saludo,
            </br>
            </br>
            {message}
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
        msg["Subject"] = "Evaluación de desempeño"
        msg["From"] = remitente
        msg["To"] = ", ".join(destinatario)

        msg.attach(MIMEText(body, "html"))

        script_directory = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_directory, "logo2.png")

        # Adjuntar la imagen del footer al mensaje
        with open(image_path, "rb") as image_file:
            footer_image = MIMEImage(image_file.read())
            footer_image.add_header("Content-ID", "<footer_image>")
            msg.attach(footer_image)

        server.sendmail(remitente, destinatario, msg.as_string())
        print("todo bien: send_email")
        server.quit()
    except Exception as ex:
        return {"La Actualizacion falló": str(ex)}