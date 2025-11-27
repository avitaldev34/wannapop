from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import smtplib
from email.mime.text import MIMEText
import os

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    # Pàgina principal
    return render_template("index.html", user=current_user)

@bp.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    """
    Pàgina de contacte.
    - GET: mostra el formulari
    - POST: envia un email als administradors
    """
    if request.method == "POST":
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not subject or not message:
            flash("Has d'omplir tots els camps!", "error")
            return redirect(url_for("main.contact"))

        # Credencials SMTP des de .env
        sender = os.getenv("MAIL_SENDER_ADDR")
        password = os.getenv("MAIL_SENDER_PASSWORD")
        smtp_server = os.getenv("MAIL_SMTP_SERVER")
        smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))

        # Llista de destinataris des de .env
        recipients_env = os.getenv("MAIL_RECIPIENTS", sender)
        recipients = [addr.strip() for addr in recipients_env.split(",")]

        # Construïm el missatge
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)  # mostrar totes les adreces al camp To

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())

            current_app.logger.info(f"Email enviat a {recipients} amb assumpte '{subject}'")

            flash("Missatge enviat correctament!", "success")
        except Exception as e:
            current_app.logger.error(f"Error enviant email: {e}")
            flash("Error enviant el missatge. Torna-ho a provar.", "error")

        return redirect(url_for("main.contact"))

    return render_template("contact.html", user=current_user)
